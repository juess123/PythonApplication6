#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAD 处理服务（同步版本）
从原 router/run_cad.py 抽取的核心处理逻辑
"""

import os
import shutil
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from common.log import log
from converters.DwgToPdf import dwg_to_pdf
from converters.DxfToDwg import dxf_to_dwg
from converters.PdfToPng import trim_png_white_border
from converters.SvgToDxf import svg_to_dxf
from core.config import settings
from core.cos_client import get_cos_client
from mq.models import MaterialItem, PositionItem
from svg_model.builder import get_svg_size_mm
from utils.generate_scr import generate_run_scr
from utils.material_export import export_material_json


@dataclass
class CadTaskResult:
    """CAD 任务处理结果"""

    success: bool
    png_key: Optional[str] = None
    pdf_key: Optional[str] = None
    error_msg: Optional[str] = None


def cleanup_temp_files(temp_base: str, keep_files: bool = False):
    """
    清理临时文件

    Args:
        temp_base: 临时文件基础目录
        keep_files: 是否保留文件（用于调试）
    """
    if keep_files:
        log.info(f"保留临时文件: {temp_base}")
        return

    try:
        if os.path.exists(temp_base):
            shutil.rmtree(temp_base, ignore_errors=True)
            log.info(f"已清理临时文件: {temp_base}")
    except Exception as e:
        log.warning(f"清理临时文件失败: {e}")


def validate_file_exists(file_path: str, description: str) -> bool:
    """
    验证文件是否存在

    Args:
        file_path: 文件路径
        description: 文件描述

    Returns:
        bool: 文件是否存在
    """
    if not os.path.exists(file_path):
        log.error(f"{description}文件不存在: {file_path}")
        return False

    size = os.path.getsize(file_path)
    log.info(f"{description}文件验证成功: {file_path}, 大小: {size} bytes")
    return True


def process_cad_task(
    svg_key: str,
    position: List[PositionItem],
    material_data: List[MaterialItem],
    order_id: str,
    thickness_data: dict
) -> CadTaskResult:
    """
    处理 CAD 转换任务：SVG -> DXF -> DWG -> PDF -> PNG -> COS

    Args:
        svg_key: SVG 文件的 COS key
        position: 位置列表
        material_data: 材料数据列表
        order_id: 订单 ID

    Returns:
        CadTaskResult: 处理结果
    """
    log.info(
        f"开始处理 CAD 任务: svg_key={svg_key}, "
        f"position 数量={len(position)}, "
        f"material_data 数量={len(material_data)}, "
        f"order_id={order_id}"
    )

    temp_base: Optional[str] = None
    cos_client = None

    try:
        # ==================== 步骤 1: 初始化 COS 客户端 ====================
        log.info("步骤 1/8: 初始化 COS 客户端")
        try:
            cos_client = get_cos_client()
            log.info("COS 客户端初始化成功")
        except Exception as e:
            log.error(f"COS 客户端初始化失败: {e}")
            return CadTaskResult(
                success=False, error_msg=f"COS 客户端初始化失败: {str(e)}"
            )

        # ==================== 步骤 2: 创建本地目录结构 ====================
        log.info("步骤 2/8: 创建本地目录结构")
        try:
            current_time = datetime.now().strftime("%Y%m%d")
            temp_base = os.path.join(settings.TEMP_DIR, current_time, order_id)
            dxf_dir = os.path.join(temp_base, "dxf")
            dwg_dir = os.path.join(temp_base, "dwg")
            pdf_dir = os.path.join(temp_base, "pdf")
            png_dir = os.path.join(temp_base, "png")
            json_dir = os.path.join(temp_base, "json")
            src_dir = os.path.join(temp_base, "src")
            svg_dir = os.path.join(temp_base, "svg")

            for dir_path in [
                temp_base,
                dxf_dir,
                dwg_dir,
                pdf_dir,
                png_dir,
                json_dir,
                src_dir,
                svg_dir,
            ]:
                os.makedirs(dir_path, exist_ok=True)

            log.info(f"目录结构创建成功: {temp_base}")
        except Exception as e:
            log.error(f"目录创建失败: {e}")
            return CadTaskResult(success=False, error_msg=f"目录创建失败: {str(e)}")

        # ==================== 步骤 3: 从 COS 下载 SVG 文件 ====================
        log.info("步骤 3/8: 从 COS 下载 SVG 文件")
        try:
            internal_svg_name = "source.svg"
            local_svg_path = os.path.join(svg_dir, internal_svg_name)

            t0 = time.perf_counter()

            download_success = cos_client.download_file(svg_key, local_svg_path)
            


            if not download_success:
                raise RuntimeError("COS 下载返回失败")

            if not validate_file_exists(local_svg_path, "SVG"):
                raise FileNotFoundError("SVG 文件下载后不存在")
            
            elapsed = time.perf_counter() - t0
            log.info(f"SVG 文件下载成功: {local_svg_path},✅，用时 {elapsed:.4f} 秒")

        except Exception as e:
            log.error(f"SVG 文件下载失败: {e}")
            cleanup_temp_files(temp_base, keep_files=settings.KEEP_TEMP_FILES)
            return CadTaskResult(success=False, error_msg=f"SVG 文件下载失败: {str(e)}")

        # ==================== 步骤 4: 转换 SVG 为 DXF ====================
        log.info("步骤 4/8: 转换 SVG 为 DXF")
        try:
            t0 = time.perf_counter()
            dxf_path = os.path.join(dxf_dir, "source.dxf")
            svg_to_dxf(local_svg_path, dxf_path)

            if not validate_file_exists(dxf_path, "DXF"):
                raise FileNotFoundError("DXF 文件未生成")
            elapsed = time.perf_counter() - t0

            log.info(f"✅用时 {elapsed:.4f} 秒,SVG 转 DXF 成功: {dxf_path},")

        except Exception as e:
            log.error(f"SVG 转 DXF 失败: {e}")
            cleanup_temp_files(temp_base, keep_files=settings.KEEP_TEMP_FILES)
            return CadTaskResult(success=False, error_msg=f"SVG 转 DXF 失败: {str(e)}")

        # ==================== 步骤 5: 转换 DXF 为 DWG ====================
        log.info("步骤 5/8: 转换 DXF 为 DWG")
        try:
            t0 = time.perf_counter()
            convert_dwg_success, dwg_file_path = dxf_to_dwg(dxf_dir, dwg_dir)

            if not convert_dwg_success or not dwg_file_path:
                raise RuntimeError("DXF 到 DWG 转换返回失败")

            if not validate_file_exists(dwg_file_path, "DWG"):
                raise FileNotFoundError("DWG 文件未生成")


            elapsed = time.perf_counter() - t0
            log.info(f"用时 {elapsed:.4f} 秒,DXF 转 DWG 成功: {dwg_file_path}")

        except Exception as e:
            log.error(f"DXF 转 DWG 失败: {e}")
            cleanup_temp_files(temp_base, keep_files=settings.KEEP_TEMP_FILES)
            return CadTaskResult(success=False, error_msg=f"DXF 转 DWG 失败: {str(e)}")

        # ==================== 步骤 6: 转换 DWG 为 PDF ====================
        log.info("步骤 6/8: 转换 DWG 为 PDF")
        try:
            w_mm, h_mm = get_svg_size_mm(local_svg_path)
            log.info(f"SVG 尺寸解析成功: width={w_mm}mm, height={h_mm}mm")
            pdf_name = f"{order_id}.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_name)

            # 将 Pydantic 模型转换为字典列表
            #material_data_dicts = [item.model_dump() for item in material_data]
            t0 = time.perf_counter()

            material_json_path = export_material_json(
                thickness_data=thickness_data,
                material_data=material_data,
                svg_width=w_mm,
                svg_height=h_mm,
                output_dir=json_dir,
                filename="source.json",
            )
            scr_path = generate_run_scr(
                output_dir=src_dir,
                dll_path=r"C:\Users\Administrator\source\repos\PythonApplication6\DLL\WindowsFormsApp1.dll",
                material_json_path=material_json_path,
                pdf_output_path=pdf_path,
            )

            log.info("开始 DWG → PDF 转换")
            pdf_result = dwg_to_pdf(dwg_file_path, pdf_path, scr_path)

            if not pdf_result:
                raise RuntimeError("DWG 到 PDF 转换返回失败")

            if not validate_file_exists(pdf_path, "PDF"):
                raise FileNotFoundError("PDF 文件未生成")
            

            elapsed = time.perf_counter() - t0
            log.info(f"✅，用时 {elapsed:.4f} 秒,DWG 转 PDF 成功: {pdf_path}")

        except Exception as e:
            log.error(f"DWG 转 PDF 失败: {e}")
            cleanup_temp_files(temp_base, keep_files=settings.KEEP_TEMP_FILES)
            return CadTaskResult(success=False, error_msg=f"DWG 转 PDF 失败: {str(e)}")

        # ==================== 步骤 7: 裁剪 PNG 白边 ====================
        log.info("步骤 7/8: 裁剪 PNG 白边")
        try:
            t0 = time.perf_counter()
            png_name = f"{order_id}.png"
            png_path = os.path.join(png_dir, png_name)

            if not validate_file_exists(png_path, "PNG"):
                raise FileNotFoundError("PNG 文件不存在，无法裁剪")

            trim_png_white_border(png_path)

            if not validate_file_exists(png_path, "PNG"):
                raise FileNotFoundError("PNG 裁剪后文件异常")

            elapsed = time.perf_counter() - t0
            log.info(f"✅，用时 {elapsed:.4f} 秒,PNG 白边裁剪成功: {png_path}")

        except Exception as e:
            log.error(f"PNG 白边裁剪失败: {e}", exc_info=True)
            cleanup_temp_files(temp_base, keep_files=settings.KEEP_TEMP_FILES)
            return CadTaskResult(success=False, error_msg=f"PNG 白边裁剪失败: {str(e)}")

        # ==================== 步骤 8: 上传 PNG 到 COS ====================
         # ==================== 步骤 8: 上传 PNG和PDF 到 COS ====================
        log.info("步骤 8/8: 上传 PNG 和 PDF 到 COS")
        try:
            png_filename = Path(png_path).name
            pdf_filename = Path(pdf_path).name

            cos_png_key = (
                f"{settings.COS_BASE_PATH}/{current_time}/{order_id}/{png_filename}"
            )
            cos_pdf_key = (
                f"{settings.COS_BASE_PATH}/{current_time}/{order_id}/{pdf_filename}"
            )

            # 使用批量上传方法同时上传 PNG 和 PDF
            file_mappings = {
                png_path: cos_png_key,
                pdf_path: cos_pdf_key,
            }

            upload_results = cos_client.batch_upload_files(file_mappings)

            uploaded_png_key = upload_results.get(png_path)
            uploaded_pdf_key = upload_results.get(pdf_path)

            if not uploaded_png_key:
                raise RuntimeError("PNG 文件上传到 COS 失败")
            if not uploaded_pdf_key:
                raise RuntimeError("PDF 文件上传到 COS 失败")

            log.info(f"PNG 上传 COS 成功: {uploaded_png_key}")
            log.info(f"PDF 上传 COS 成功: {uploaded_pdf_key}")
            #temp_base
            # ==================== 清理临时文件 ====================False
            cleanup_temp_files(temp_base, keep_files=True)

            # ==================== 返回成功结果 ====================
            log.info(f"CAD 转换流程完成: {order_id}")
            return CadTaskResult(
                success=True, png_key=uploaded_png_key, pdf_key=uploaded_pdf_key
            )
        except Exception as e:
            log.error(f"文件上传 COS 失败: {e}")
            cleanup_temp_files(temp_base, keep_files=settings.KEEP_TEMP_FILES)
            return CadTaskResult(
                success=False, error_msg=f"文件上传 COS 失败: {str(e)}"
            )
    
    except Exception as e:
        log.error(f"CAD 转换过程发生未知错误: {e}", exc_info=True)
        if temp_base:
            cleanup_temp_files(temp_base, keep_files=settings.KEEP_TEMP_FILES)
        return CadTaskResult(success=False, error_msg=f"CAD 转换失败: {str(e)}")
