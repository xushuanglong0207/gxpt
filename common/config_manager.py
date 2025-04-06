#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from dotenv import load_dotenv


class ConfigManager:
    """配置管理类，负责加载和管理不同环境的配置"""
    
    def __init__(self, env="test"):
        """
        初始化配置管理器
        
        Args:
            env: 环境名称，可选值为 dev, test, prod
        """
        self.env = env
        self.config = {}
        
        # 加载环境变量
        self._load_env_vars()
        
        # 加载配置文件
        self._load_config_files()
    
    def _load_env_vars(self):
        """加载环境变量"""
        # 加载.env文件中的环境变量
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        if os.path.exists(env_file):
            load_dotenv(env_file)
    
    def _load_config_files(self):
        """加载配置文件"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(base_dir, 'config')
        
        # 加载通用配置
        common_config_file = os.path.join(config_dir, 'config.yaml')
        if os.path.exists(common_config_file):
            with open(common_config_file, 'r', encoding='utf-8') as f:
                self.config.update(yaml.safe_load(f))
        
        # 加载环境特定配置
        env_config_file = os.path.join(config_dir, f'config_{self.env}.yaml')
        if os.path.exists(env_config_file):
            with open(env_config_file, 'r', encoding='utf-8') as f:
                env_config = yaml.safe_load(f)
                # 递归合并配置
                self._merge_config(self.config, env_config)
        
        # 加载模块特定配置
        modules_config_dir = os.path.join(config_dir, 'modules')
        if os.path.exists(modules_config_dir):
            for module_file in os.listdir(modules_config_dir):
                if module_file.endswith('.yaml'):
                    module_path = os.path.join(modules_config_dir, module_file)
                    with open(module_path, 'r', encoding='utf-8') as f:
                        module_config = yaml.safe_load(f)
                        # 将模块配置添加到主配置中
                        module_name = os.path.splitext(module_file)[0]
                        if 'modules' not in self.config:
                            self.config['modules'] = {}
                        self.config['modules'][module_name] = module_config
    
    def _merge_config(self, base, override):
        """递归合并配置字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key, default=None):
        """
        获取配置项
        
        Args:
            key: 配置键，支持点号分隔的多级键，如 'api.base_url'
            default: 默认值，当配置项不存在时返回
            
        Returns:
            配置值或默认值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_all(self):
        """获取所有配置"""
        return self.config
    
    def get_env(self):
        """获取当前环境名称"""
        return self.env
    
    def get_api_config(self):
        """获取API测试相关配置"""
        return self.get('api', {})
    
    def get_ui_config(self):
        """获取UI测试相关配置"""
        return self.get('ui', {})
    
    def get_ssh_config(self):
        """获取SSH测试相关配置"""
        return self.get('ssh', {})
    
    def get_module_config(self, module_name):
        """
        获取指定模块的配置
        
        Args:
            module_name: 模块名称，如 'api.user', 'ui.login'
            
        Returns:
            模块配置字典
        """
        return self.get(f'modules.{module_name}', {})
    
    def get_modules_list(self, module_type=None):
        """
        获取所有模块列表
        
        Args:
            module_type: 模块类型，如 'api', 'ui', 'ssh'，为None时返回所有模块
            
        Returns:
            模块列表
        """
        modules = self.get('modules', {})
        if not module_type:
            return list(modules.keys())
        
        return [m for m in modules.keys() if m.startswith(f"{module_type}.")] 