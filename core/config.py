from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # ========== 腾讯云 COS 配置 ==========
    COS_SECRET_ID: str
    COS_SECRET_KEY: str
    COS_REGION: str = "ap-shanghai"
    COS_BUCKET: str
    COS_SCHEME: str = "https"
    COS_CDN_DOMAIN: str = ""  # CDN加速域名（可选）
    COS_BASE_PATH: str = "cad"  # COS中的基础路径

    # ========== 日志配置 ==========
    LOG_DIR: str = "./logs"
    LOG_LEVEL: str = "INFO"

    # ========== 临时目录配置 ==========
    TEMP_DIR: str = "./temp"
    KEEP_TEMP_FILES: bool = True

    # ========== RabbitMQ 配置 ==========
    RABBITMQ_HOST: str = "127.0.0.1"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USERNAME: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    RABBITMQ_QUEUE_NAME: str = "cad_task"  # 监听的队列名称

    # ========== 回调配置 ==========
    CALLBACK_TIMEOUT: float = 30.0  # 回调请求超时时间（秒）
    CALLBACK_MAX_RETRIES: int = 3  # 回调最大重试次数


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 导出配置实例
settings = get_settings()
