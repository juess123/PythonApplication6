#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯云COS客户端封装
"""
import os
from typing import Optional
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError

from common.log import log
from core.config import settings


class COSClient:
    """腾讯云COS客户端"""
    
    def __init__(self):
        """初始化COS客户端"""
        self.region = settings.COS_REGION
        self.secret_id = settings.COS_SECRET_ID
        self.secret_key = settings.COS_SECRET_KEY
        self.bucket = settings.COS_BUCKET
        self.scheme = settings.COS_SCHEME
        
        # 配置COS客户端
        config = CosConfig(
            Region=self.region,
            SecretId=self.secret_id,
            SecretKey=self.secret_key,
            Scheme=self.scheme
        )
        self.client = CosS3Client(config)
        log.debug(f"COS客户端初始化成功: bucket={self.bucket}, region={self.region}")
    
    def download_file(self, cos_key: str, local_path: str) -> bool:
        """
        从COS下载文件到本地
        
        Args:
            cos_key: COS对象键（路径）
            local_path: 本地保存路径
            
        Returns:
            bool: 下载是否成功
        """
        try:
            # 确保本地目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            log.debug(f"开始从COS下载文件: {cos_key} -> {local_path}")
            
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=cos_key
            )
            
            # 保存文件
            response['Body'].get_stream_to_file(local_path)
            
            file_size = os.path.getsize(local_path)
            log.debug(f"文件下载成功: {local_path}, 大小: {file_size} bytes")
            return True
            
        except CosServiceError as e:
            log.error(f"COS服务错误: {e.get_error_code()} - {e.get_error_msg()}")
            log.error(f"Request ID: {e.get_request_id()}, Resource: {e.get_resource_location()}")
            return False
        except CosClientError as e:
            log.error(f"COS客户端错误: {e}")
            return False
        except Exception as e:
            log.error(f"下载文件时发生未知错误: {e}", exc_info=True)
            return False
    
    def upload_file(self, local_path: str, cos_key: str) -> Optional[str]:
        """
        上传文件到COS
        
        Args:
            local_path: 本地文件路径
            cos_key: COS对象键（路径）
            
        Returns:
            Optional[str]: 上传成功返回COS key，失败返回None
        """
        try:
            if not os.path.exists(local_path):
                log.error(f"本地文件不存在: {local_path}")
                return None
            
            file_size = os.path.getsize(local_path)
            log.info(f"开始上传文件到COS: {local_path} -> {cos_key}, 大小: {file_size} bytes")
            
            # 使用高级上传接口（自动分块上传大文件）
            response = self.client.upload_file(
                Bucket=self.bucket,
                Key=cos_key,
                LocalFilePath=local_path,
                EnableMD5=False
            )
            
            log.info(f"文件上传成功: {cos_key}, ETag: {response.get('ETag', 'N/A')}")
            return cos_key
            
        except CosServiceError as e:
            log.error(f"COS服务错误: {e.get_error_code()} - {e.get_error_msg()}")
            log.error(f"Request ID: {e.get_request_id()}")
            return None
        except CosClientError as e:
            log.error(f"COS客户端错误: {e}")
            return None
        except Exception as e:
            log.error(f"上传文件时发生未知错误: {e}", exc_info=True)
            return None
    
    def batch_upload_files(self, file_mappings: dict) -> dict:
        """
        批量上传文件
        
        Args:
            file_mappings: {local_path: cos_key} 映射字典
            
        Returns:
            dict: {local_path: cos_key or None} 上传结果
        """
        results = {}
        for local_path, cos_key in file_mappings.items():
            result = self.upload_file(local_path, cos_key)
            results[local_path] = result
        return results
    
    def get_file_url(self, cos_key: str) -> str:
        """
        获取COS文件的访问URL
        
        Args:
            cos_key: COS对象键
            
        Returns:
            str: 文件访问URL
        """
        # 如果配置了CDN域名，使用CDN域名
        if hasattr(settings, 'COS_CDN_DOMAIN') and settings.COS_CDN_DOMAIN:
            return f"{settings.COS_CDN_DOMAIN}/{cos_key}"
        
        # 否则使用默认域名
        return f"{self.scheme}://{self.bucket}.cos.{self.region}.myqcloud.com/{cos_key}"
    
    def delete_file(self, cos_key: str) -> bool:
        """
        删除COS文件
        
        Args:
            cos_key: COS对象键
            
        Returns:
            bool: 删除是否成功
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=cos_key
            )
            log.info(f"文件删除成功: {cos_key}")
            return True
        except Exception as e:
            log.error(f"删除文件失败: {cos_key}, 错误: {e}")
            return False


# 全局COS客户端实例
cos_client: Optional[COSClient] = None


def get_cos_client() -> COSClient:
    """获取COS客户端实例（单例模式）"""
    global cos_client
    if cos_client is None:
        cos_client = COSClient()
    return cos_client
