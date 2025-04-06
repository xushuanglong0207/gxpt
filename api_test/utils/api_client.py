#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from typing import Dict, Any, Optional, Union
from requests.exceptions import RequestException

from common.utils.logger import log
from common.utils.config_loader import config


class APIClient:
    """API测试客户端，用于发送API请求并处理响应"""

    def __init__(self):
        """初始化API客户端"""
        # 获取API配置
        api_config = config.get_env_config("api")
        self.base_url = api_config.get("base_url", "")
        self.timeout = api_config.get("timeout", 10)
        self.headers = api_config.get("headers", {})
        
        # 创建会话
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        log.info(f"API客户端初始化完成，基础URL: {self.base_url}")

    def get(self, path: str, params: Dict = None, headers: Dict = None, **kwargs) -> Dict[str, Any]:
        """发送GET请求
        
        Args:
            path: API路径
            params: 查询参数
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        return self._request("GET", path, params=params, headers=headers, **kwargs)

    def post(self, path: str, data: Dict = None, json_data: Dict = None, headers: Dict = None, **kwargs) -> Dict[str, Any]:
        """发送POST请求
        
        Args:
            path: API路径
            data: 表单数据
            json_data: JSON数据
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        return self._request("POST", path, data=data, json=json_data, headers=headers, **kwargs)

    def put(self, path: str, data: Dict = None, json_data: Dict = None, headers: Dict = None, **kwargs) -> Dict[str, Any]:
        """发送PUT请求
        
        Args:
            path: API路径
            data: 表单数据
            json_data: JSON数据
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        return self._request("PUT", path, data=data, json=json_data, headers=headers, **kwargs)

    def delete(self, path: str, headers: Dict = None, **kwargs) -> Dict[str, Any]:
        """发送DELETE请求
        
        Args:
            path: API路径
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        return self._request("DELETE", path, headers=headers, **kwargs)

    def patch(self, path: str, data: Dict = None, json_data: Dict = None, headers: Dict = None, **kwargs) -> Dict[str, Any]:
        """发送PATCH请求
        
        Args:
            path: API路径
            data: 表单数据
            json_data: JSON数据
            headers: 请求头
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        return self._request("PATCH", path, data=data, json=json_data, headers=headers, **kwargs)

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """发送请求
        
        Args:
            method: 请求方法
            path: API路径
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 响应数据
        """
        # 合并请求头
        headers = kwargs.pop("headers", {})
        if headers:
            headers = {**self.headers, **headers}
        else:
            headers = self.headers
        
        # 构建完整URL
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        
        # 设置超时
        timeout = kwargs.pop("timeout", self.timeout)
        
        log.info(f"发送 {method} 请求: {url}")
        log.debug(f"请求参数: {kwargs}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
            
            # 尝试解析JSON响应
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"text": response.text}
            
            log.info(f"响应状态码: {response.status_code}")
            log.debug(f"响应数据: {response_data}")
            
            # 添加状态码到响应数据
            response_data["status_code"] = response.status_code
            
            return response_data
        
        except RequestException as e:
            log.error(f"请求异常: {e}")
            return {"error": str(e), "status_code": 0}

    def set_token(self, token: str, token_type: str = "Bearer") -> None:
        """设置认证令牌
        
        Args:
            token: 令牌字符串
            token_type: 令牌类型，默认为Bearer
        """
        self.session.headers.update({"Authorization": f"{token_type} {token}"})
        log.info("认证令牌已设置")

    def clear_token(self) -> None:
        """清除认证令牌"""
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
            log.info("认证令牌已清除")


# 创建全局API客户端实例
api_client = APIClient() 