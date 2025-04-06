#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import pytest
import requests
from datetime import datetime
from loguru import logger
from concurrent.futures import ThreadPoolExecutor


class ApiTestRunner:
    """API测试运行器，用于执行API自动化测试"""
    
    def __init__(self, config, parallel=1, tags=None, submodule=None):
        """
        初始化API测试运行器
        
        Args:
            config: 配置管理器实例
            parallel: 并行执行的线程数
            tags: 要执行的测试标签
            submodule: 要执行的子模块，如 'user', 'order' 等
        """
        self.config = config
        self.parallel = parallel
        self.tags = tags
        self.submodule = submodule
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.api_config = config.get_api_config()
        self.base_url = self.api_config.get('base_url', '')
        self.timeout = self.api_config.get('timeout', 30)
        self.headers = self.api_config.get('headers', {})
        
        # 如果指定了子模块，加载子模块配置
        if submodule:
            module_config = config.get_module_config(f'api.{submodule}')
            if module_config:
                # 更新基础配置
                if 'base_url' in module_config:
                    self.base_url = module_config['base_url']
                if 'timeout' in module_config:
                    self.timeout = module_config['timeout']
                if 'headers' in module_config:
                    self.headers.update(module_config.get('headers', {}))
    
    def run(self):
        """
        运行API测试
        
        Returns:
            测试结果列表
        """
        logger.info("开始执行API测试")
        if self.submodule:
            logger.info(f"子模块: {self.submodule}")
        
        # 获取测试用例
        test_cases = self._get_test_cases()
        logger.info(f"找到 {len(test_cases)} 个API测试用例")
        
        # 如果没有测试用例，返回空列表
        if not test_cases:
            logger.warning("没有找到符合条件的API测试用例")
            return []
        
        # 执行测试用例
        results = []
        if self.parallel > 1 and len(test_cases) > 1:
            # 并行执行
            logger.info(f"使用 {self.parallel} 个线程并行执行API测试")
            with ThreadPoolExecutor(max_workers=self.parallel) as executor:
                futures = [executor.submit(self._execute_test_case, test_case) for test_case in test_cases]
                for future in futures:
                    result = future.result()
                    if result:
                        results.append(result)
        else:
            # 串行执行
            logger.info("串行执行API测试")
            for test_case in test_cases:
                result = self._execute_test_case(test_case)
                if result:
                    results.append(result)
        
        logger.info(f"API测试执行完成，共 {len(results)} 个结果")
        return results
    
    def _get_test_cases(self):
        """获取测试用例"""
        test_cases = []
        
        # 确定测试用例目录
        if self.submodule:
            test_dir = os.path.join(self.base_dir, "testcases", self.submodule)
        else:
            test_dir = os.path.join(self.base_dir, "testcases")
        
        # 如果测试用例目录不存在，返回空列表
        if not os.path.exists(test_dir):
            logger.warning(f"测试用例目录不存在: {test_dir}")
            return []
        
        # 遍历测试用例目录
        for root, _, files in os.walk(test_dir):
            for file in files:
                # 只处理JSON文件
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            test_case = json.load(f)
                        
                        # 如果指定了标签，检查测试用例是否包含该标签
                        if self.tags and not self._match_tags(test_case.get("tags", [])):
                            continue
                        
                        # 添加子模块信息
                        if self.submodule:
                            test_case["submodule"] = self.submodule
                        else:
                            # 从路径中提取子模块
                            rel_path = os.path.relpath(file_path, os.path.join(self.base_dir, "testcases"))
                            parts = os.path.dirname(rel_path).split(os.sep)
                            if parts and parts[0]:
                                test_case["submodule"] = parts[0]
                        
                        test_case["file_path"] = file_path
                        test_cases.append(test_case)
                    except Exception as e:
                        logger.error(f"加载测试用例失败: {file_path}, 错误: {str(e)}")
        
        return test_cases
    
    def _match_tags(self, case_tags):
        """检查测试用例标签是否匹配"""
        if not self.tags:
            return True
        
        # 将标签字符串拆分为列表
        tag_list = self.tags.split(",") if isinstance(self.tags, str) else self.tags
        
        # 检查是否有任何一个标签匹配
        for tag in tag_list:
            if tag.strip() in case_tags:
                return True
        
        return False
    
    def _execute_test_case(self, test_case):
        """
        执行单个测试用例
        
        Args:
            test_case: 测试用例数据
            
        Returns:
            测试结果字典
        """
        name = test_case.get("name", "未命名测试")
        description = test_case.get("description", "")
        method = test_case.get("method", "GET").upper()
        endpoint = test_case.get("endpoint", "")
        headers = {**self.headers, **test_case.get("headers", {})}
        params = test_case.get("params", {})
        data = test_case.get("data", {})
        json_data = test_case.get("json", None)
        expected_status = test_case.get("expected_status", 200)
        expected_response = test_case.get("expected_response", None)
        validate_schema = test_case.get("validate_schema", None)
        submodule = test_case.get("submodule", "")
        
        # 构建完整URL
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}" if endpoint else self.base_url
        
        # 初始化结果
        result = {
            "name": name,
            "description": description,
            "module": "api",
            "submodule": submodule,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "start_timestamp": int(time.time() * 1000),
            "status": "skipped",
            "duration": 0,
            "error": "",
            "traceback": "",
            "request": {
                "method": method,
                "url": url,
                "headers": headers,
                "params": params,
                "data": data,
                "json": json_data
            },
            "response": {}
        }
        
        try:
            logger.info(f"执行API测试: {name}")
            logger.debug(f"请求: {method} {url}")
            
            # 记录开始时间
            start_time = time.time()
            
            # 发送请求
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=self.timeout
            )
            
            # 计算耗时
            duration = time.time() - start_time
            result["duration"] = duration
            
            # 记录响应
            result["response"] = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
            }
            
            try:
                result["response"]["json"] = response.json()
            except:
                pass
            
            # 验证状态码
            if response.status_code != expected_status:
                result["status"] = "failed"
                result["error"] = f"状态码不匹配: 期望 {expected_status}, 实际 {response.status_code}"
                logger.error(f"测试失败: {name}, {result['error']}")
                return result
            
            # 验证响应内容
            if expected_response:
                try:
                    response_json = response.json()
                    for key, value in expected_response.items():
                        if key not in response_json or response_json[key] != value:
                            result["status"] = "failed"
                            result["error"] = f"响应内容不匹配: 键 '{key}' 期望值 '{value}', 实际值 '{response_json.get(key, 'missing')}'"
                            logger.error(f"测试失败: {name}, {result['error']}")
                            return result
                except Exception as e:
                    result["status"] = "failed"
                    result["error"] = f"验证响应内容失败: {str(e)}"
                    result["traceback"] = str(e)
                    logger.error(f"测试失败: {name}, {result['error']}")
                    return result
            
            # 验证JSON Schema
            if validate_schema:
                try:
                    from jsonschema import validate
                    response_json = response.json()
                    validate(instance=response_json, schema=validate_schema)
                except Exception as e:
                    result["status"] = "failed"
                    result["error"] = f"JSON Schema验证失败: {str(e)}"
                    result["traceback"] = str(e)
                    logger.error(f"测试失败: {name}, {result['error']}")
                    return result
            
            # 测试通过
            result["status"] = "passed"
            logger.info(f"测试通过: {name}, 耗时: {duration:.2f}秒")
        
        except Exception as e:
            # 测试执行异常
            result["status"] = "failed"
            result["error"] = f"测试执行异常: {str(e)}"
            result["traceback"] = str(e)
            logger.error(f"测试执行异常: {name}, 错误: {str(e)}")
        
        # 记录结束时间
        result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result["end_timestamp"] = int(time.time() * 1000)
        
        return result 