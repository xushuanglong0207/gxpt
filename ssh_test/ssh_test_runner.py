#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import traceback
import warnings
from datetime import datetime
from loguru import logger
import paramiko
from concurrent.futures import ThreadPoolExecutor

# 抑制 cryptography 的弃用警告
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=".*TripleDES has been moved to cryptography.hazmat.decrepit.*"
)
warnings.filterwarnings(
    "ignore", 
    category=DeprecationWarning, 
    module="paramiko.*"
)

class SshTestRunner:
    """SSH测试运行器，用于执行SSH自动化测试"""
    
    def __init__(self, config, parallel=1, tags=None, submodule=None):
        """
        初始化SSH测试运行器
        
        Args:
            config: 配置管理器实例
            parallel: 并行执行的线程数
            tags: 要执行的测试标签
            submodule: 要执行的子模块，如 'server', 'database' 等
        """
        self.config = config
        self.parallel = parallel
        self.tags = tags
        self.submodule = submodule
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ssh_config = config.get_ssh_config()
        self.timeout = self.ssh_config.get('timeout', 30)
        self.log_dir = os.path.join(self.base_dir, "logs")
        
        # 如果指定了子模块，加载子模块配置
        if submodule:
            module_config = config.get_module_config(f'ssh.{submodule}')
            if module_config:
                # 更新基础配置
                if 'timeout' in module_config:
                    self.timeout = module_config['timeout']
                if 'default_servers' in module_config:
                    self.default_servers = module_config['default_servers']
        
        # 确保日志目录存在
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def run(self):
        """
        运行SSH测试
        
        Returns:
            测试结果列表
        """
        logger.info("开始执行SSH测试")
        if self.submodule:
            logger.info(f"子模块: {self.submodule}")
        
        # 获取测试用例
        test_cases = self._get_test_cases()
        logger.info(f"找到 {len(test_cases)} 个SSH测试用例")
        
        # 如果没有测试用例，返回空列表
        if not test_cases:
            logger.warning("没有找到符合条件的SSH测试用例")
            return []
        
        # 执行测试用例
        results = []
        if self.parallel > 1 and len(test_cases) > 1:
            # 并行执行
            logger.info(f"使用 {self.parallel} 个线程并行执行SSH测试")
            with ThreadPoolExecutor(max_workers=self.parallel) as executor:
                futures = [executor.submit(self._execute_test_case, test_case) for test_case in test_cases]
                for future in futures:
                    result = future.result()
                    if result:
                        results.append(result)
        else:
            # 串行执行
            logger.info("串行执行SSH测试")
            for test_case in test_cases:
                result = self._execute_test_case(test_case)
                if result:
                    results.append(result)
        
        logger.info(f"SSH测试执行完成，共 {len(results)} 个结果")
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
    
    def _create_ssh_client(self, host, port, username, password=None, key_file=None):
        """
        创建SSH客户端连接
        
        Args:
            host: 主机地址
            port: 端口
            username: 用户名
            password: 密码
            key_file: 密钥文件路径
            
        Returns:
            SSH客户端实例
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            if key_file:
                # 使用密钥文件连接
                key = paramiko.RSAKey.from_private_key_file(key_file)
                client.connect(hostname=host, port=port, username=username, pkey=key, timeout=self.timeout)
            else:
                # 使用密码连接
                client.connect(hostname=host, port=port, username=username, password=password, timeout=self.timeout)
            
            return client
        except Exception as e:
            logger.error(f"SSH连接失败: {host}:{port}, 错误: {str(e)}")
            raise
    
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
        host = test_case.get("host", "")
        port = test_case.get("port", 22)
        username = test_case.get("username", "")
        password = test_case.get("password", "")
        key_file = test_case.get("key_file", "")
        commands = test_case.get("commands", [])
        expected_results = test_case.get("expected_results", {})
        submodule = test_case.get("submodule", "")
        
        # 初始化结果
        result = {
            "name": name,
            "description": description,
            "module": "ssh",
            "submodule": submodule,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "start_timestamp": int(time.time() * 1000),
            "status": "skipped",
            "duration": 0,
            "error": "",
            "traceback": "",
            "command_results": []
        }
        
        client = None
        try:
            logger.info(f"执行SSH测试: {name}")
            logger.debug(f"连接到: {username}@{host}:{port}")
            
            # 记录开始时间
            start_time = time.time()
            
            # 创建SSH客户端连接
            client = self._create_ssh_client(host, port, username, password, key_file)
            
            # 执行命令
            for i, command in enumerate(commands):
                cmd_name = command.get("name", f"命令 {i+1}")
                cmd_value = command.get("command", "")
                cmd_timeout = command.get("timeout", self.timeout)
                
                logger.debug(f"执行命令: {cmd_name}: {cmd_value}")
                
                # 执行命令
                stdin, stdout, stderr = client.exec_command(cmd_value, timeout=cmd_timeout)
                
                # 获取输出
                stdout_str = stdout.read().decode('utf-8')
                stderr_str = stderr.read().decode('utf-8')
                exit_code = stdout.channel.recv_exit_status()
                
                # 记录命令结果
                cmd_result = {
                    "name": cmd_name,
                    "command": cmd_value,
                    "stdout": stdout_str,
                    "stderr": stderr_str,
                    "exit_code": exit_code,
                    "status": "passed"
                }
                
                # 验证预期结果
                if cmd_name in expected_results:
                    expected = expected_results[cmd_name]
                    
                    # 验证退出码
                    if "exit_code" in expected and expected["exit_code"] != exit_code:
                        cmd_result["status"] = "failed"
                        cmd_result["error"] = f"退出码不匹配: 期望 {expected['exit_code']}, 实际 {exit_code}"
                    
                    # 验证标准输出
                    if "stdout" in expected:
                        if isinstance(expected["stdout"], list):
                            # 检查每一行是否都在输出中
                            for line in expected["stdout"]:
                                if line not in stdout_str:
                                    cmd_result["status"] = "failed"
                                    cmd_result["error"] = f"标准输出不匹配: 期望包含 '{line}'"
                                    break
                        else:
                            # 检查整个字符串是否在输出中
                            if expected["stdout"] not in stdout_str:
                                cmd_result["status"] = "failed"
                                cmd_result["error"] = f"标准输出不匹配: 期望包含 '{expected['stdout']}'"
                    
                    # 验证标准错误
                    if "stderr" in expected:
                        if isinstance(expected["stderr"], list):
                            # 检查每一行是否都在输出中
                            for line in expected["stderr"]:
                                if line not in stderr_str:
                                    cmd_result["status"] = "failed"
                                    cmd_result["error"] = f"标准错误不匹配: 期望包含 '{line}'"
                                    break
                        else:
                            # 检查整个字符串是否在输出中
                            if expected["stderr"] not in stderr_str:
                                cmd_result["status"] = "failed"
                                cmd_result["error"] = f"标准错误不匹配: 期望包含 '{expected['stderr']}'"
                
                # 添加到结果列表
                result["command_results"].append(cmd_result)
                
                # 如果命令失败，整个测试失败
                if cmd_result["status"] == "failed":
                    result["status"] = "failed"
                    result["error"] = f"命令 '{cmd_name}' 执行失败: {cmd_result.get('error', '')}"
                    logger.error(f"测试失败: {name}, {result['error']}")
                    break
            
            # 计算耗时
            duration = time.time() - start_time
            result["duration"] = duration
            
            # 如果没有失败的命令，测试通过
            if result["status"] != "failed":
                result["status"] = "passed"
                logger.info(f"测试通过: {name}, 耗时: {duration:.2f}秒")
        
        except Exception as e:
            # 测试执行异常
            result["status"] = "failed"
            result["error"] = f"测试执行异常: {str(e)}"
            result["traceback"] = traceback.format_exc()
            logger.error(f"测试执行异常: {name}, 错误: {str(e)}")
        
        finally:
            # 关闭SSH连接
            if client:
                client.close()
            
            # 记录结束时间
            result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result["end_timestamp"] = int(time.time() * 1000)
            
            # 保存命令输出到日志文件
            self._save_command_logs(name, result["command_results"])
        
        return result
    
    def _save_command_logs(self, test_name, command_results):
        """
        保存命令输出到日志文件
        
        Args:
            test_name: 测试名称
            command_results: 命令结果列表
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.log".replace(" ", "_")
        filepath = os.path.join(self.log_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"SSH测试: {test_name}\n")
                f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                for i, cmd_result in enumerate(command_results):
                    f.write(f"命令 {i+1}: {cmd_result['name']}\n")
                    f.write(f"命令行: {cmd_result['command']}\n")
                    f.write(f"状态: {cmd_result['status']}\n")
                    f.write(f"退出码: {cmd_result['exit_code']}\n")
                    
                    if cmd_result.get("error"):
                        f.write(f"错误: {cmd_result['error']}\n")
                    
                    f.write("\n标准输出:\n")
                    f.write("-"*80 + "\n")
                    f.write(cmd_result['stdout'])
                    f.write("\n\n标准错误:\n")
                    f.write("-"*80 + "\n")
                    f.write(cmd_result['stderr'])
                    f.write("\n\n" + "="*80 + "\n\n")
            
            logger.debug(f"命令日志已保存: {filepath}")
        except Exception as e:
            logger.error(f"保存命令日志失败: {str(e)}") 