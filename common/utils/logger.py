#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
from loguru import logger
from typing import Dict, Any

# 尝试导入配置，如果失败则使用默认配置
try:
    from common.utils.config_loader import config
    log_config = config.get_global_config()
except ImportError:
    log_config = {
        "log_level": "INFO",
        "log_path": "./logs"
    }

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": "DEBUG",
    "INFO": "INFO",
    "WARNING": "WARNING",
    "ERROR": "ERROR",
    "CRITICAL": "CRITICAL"
}


class Logger:
    """日志工具类"""

    def __init__(self):
        """初始化日志配置"""
        self.log_level = LOG_LEVELS.get(log_config.get("log_level", "INFO"), "INFO")
        self.log_path = log_config.get("log_path", "./logs")
        
        # 创建日志目录
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        
        # 生成日志文件名
        self.log_file = os.path.join(
            self.log_path,
            f"test_{time.strftime('%Y%m%d_%H%M%S')}.log"
        )
        
        # 配置日志
        self._configure_logger()

    def _configure_logger(self):
        """配置日志器"""
        # 移除默认处理器
        logger.remove()
        
        # 添加控制台处理器
        logger.add(
            sys.stdout,
            level=self.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # 添加文件处理器
        logger.add(
            self.log_file,
            level=self.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="1 week",
            encoding="utf-8"
        )
    
    def get_logger(self):
        """获取日志器
        
        Returns:
            logger: 日志器实例
        """
        return logger


# 创建全局日志实例
log = Logger().get_logger() 