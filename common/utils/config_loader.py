#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from loguru import logger
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器，用于读取和管理配置信息"""

    _instance = None
    _config = None

    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = None):
        """初始化配置加载器
        
        Args:
            config_path: 配置文件路径，默认为 config/config.yaml
        """
        if ConfigLoader._config is None:
            self.config_path = config_path or os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "config",
                "config.yaml"
            )
            self.load_config()

    def load_config(self) -> None:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                ConfigLoader._config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {self.config_path}")
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            ConfigLoader._config = {}

    def get_config(self) -> Dict[str, Any]:
        """获取全部配置
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return ConfigLoader._config

    def get_environment(self) -> str:
        """获取当前环境
        
        Returns:
            str: 环境名称 (dev, test, prod)
        """
        return ConfigLoader._config.get('global', {}).get('environment', 'test')

    def get_env_config(self, module: str = None) -> Dict[str, Any]:
        """获取当前环境的配置
        
        Args:
            module: 模块名称 (api, ui, ssh)
            
        Returns:
            Dict[str, Any]: 环境配置
        """
        env = self.get_environment()
        env_config = ConfigLoader._config.get('environments', {}).get(env, {})
        
        if module and module in env_config:
            return env_config[module]
        return env_config

    def get_test_data(self, module: str = None) -> Dict[str, Any]:
        """获取测试数据
        
        Args:
            module: 模块名称 (api, ui, ssh)
            
        Returns:
            Dict[str, Any]: 测试数据
        """
        test_data = ConfigLoader._config.get('test_data', {})
        
        if module and module in test_data:
            return test_data[module]
        return test_data

    def get_global_config(self, key: str = None) -> Any:
        """获取全局配置
        
        Args:
            key: 配置键名
            
        Returns:
            Any: 配置值
        """
        global_config = ConfigLoader._config.get('global', {})
        
        if key and key in global_config:
            return global_config[key]
        return global_config


# 创建全局配置实例
config = ConfigLoader() 