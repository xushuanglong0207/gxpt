#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 首先导入警告抑制模块
import suppress_warnings

import argparse
import os
import sys
import time
import warnings
from loguru import logger

# 抑制 cryptography 的弃用警告
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=".*TripleDES has been moved to cryptography.hazmat.decrepit.*"
)

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.config_manager import ConfigManager
from common.report_generator import ReportGenerator
from api_test.api_test_runner import ApiTestRunner
from ui_test.ui_test_runner import UiTestRunner
from ssh_test.ssh_test_runner import SshTestRunner

# 从环境变量获取配置
def get_env_config():
    """获取环境变量配置"""
    return {
        'FLASK_ENV': os.getenv('FLASK_ENV', 'production'),
        'DATABASE_URL': os.getenv('DATABASE_URL', 'mysql://test_user:test_password@db:3306/test_platform'),
        'PORT': int(os.getenv('PORT', 8089)),
        'HOST': os.getenv('HOST', '0.0.0.0')  # 在Docker中需要监听所有接口
    }

def setup_logger():
    """配置日志"""
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    
    log_file = os.path.join(log_path, f"test_{time.strftime('%Y%m%d_%H%M%S')}.log")
    logger.add(log_file, rotation="100 MB", retention="30 days", level="INFO")
    return logger


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="高效测试平台")
    parser.add_argument("--module", choices=["api", "ui", "ssh", "all"], default="all",
                        help="指定要运行的测试模块: api, ui, ssh 或 all")
    parser.add_argument("--submodule", type=str,
                        help="指定要运行的子模块，如 'api.user', 'ui.login', 'ssh.server'")
    parser.add_argument("--env", choices=["dev", "test", "prod"], default="test",
                        help="指定测试环境: dev, test 或 prod")
    parser.add_argument("--report", choices=["html", "allure", "json"], default="html",
                        help="指定报告类型: html, allure 或 json")
    parser.add_argument("--parallel", type=int, default=1,
                        help="并行执行的进程数")
    parser.add_argument("--tags", type=str, help="指定要运行的标签")
    parser.add_argument("--list-modules", action="store_true",
                        help="列出所有可用的模块和子模块")
    
    return parser.parse_args()


def list_modules(config):
    """列出所有可用的模块和子模块"""
    logger.info("可用的模块和子模块:")
    
    # 获取所有模块
    api_modules = config.get_modules_list("api")
    ui_modules = config.get_modules_list("ui")
    ssh_modules = config.get_modules_list("ssh")
    
    # 打印API模块
    logger.info("API模块:")
    if api_modules:
        for module in api_modules:
            logger.info(f"  - {module}")
    else:
        logger.info("  - 无可用子模块")
    
    # 打印UI模块
    logger.info("UI模块:")
    if ui_modules:
        for module in ui_modules:
            logger.info(f"  - {module}")
    else:
        logger.info("  - 无可用子模块")
    
    # 打印SSH模块
    logger.info("SSH模块:")
    if ssh_modules:
        for module in ssh_modules:
            logger.info(f"  - {module}")
    else:
        logger.info("  - 无可用子模块")


def main():
    """主函数"""
    # 获取环境配置
    env_config = get_env_config()
    
    # 设置日志
    logger = setup_logger()
    logger.info("开始执行自动化测试")
    logger.info(f"环境配置: {env_config}")
    
    # 解析命令行参数
    args = parse_args()
    logger.info(f"运行参数: {args}")
    
    # 加载配置
    config = ConfigManager(args.env)
    logger.info(f"加载配置: {args.env}")
    
    # 如果指定了列出模块，则列出所有模块并退出
    if args.list_modules:
        list_modules(config)
        return 0
    
    # 处理子模块参数
    module_type = None
    submodule = None
    if args.submodule:
        parts = args.submodule.split('.')
        if len(parts) >= 2:
            module_type = parts[0]
            submodule = '.'.join(parts[1:])
        else:
            logger.warning(f"子模块格式不正确: {args.submodule}，应为 'module_type.submodule'")
            return 1
    
    # 初始化报告生成器
    report_generator = ReportGenerator(args.report)
    
    # 根据模块选择运行不同的测试
    results = []
    
    try:
        # 如果指定了子模块，只运行该子模块
        if module_type:
            if module_type == "api":
                logger.info(f"开始执行API子模块测试: {submodule}")
                api_runner = ApiTestRunner(config, parallel=args.parallel, tags=args.tags, submodule=submodule)
                api_results = api_runner.run()
                results.extend(api_results)
                logger.info(f"API子模块测试执行完成: {submodule}")
            elif module_type == "ui":
                logger.info(f"开始执行UI子模块测试: {submodule}")
                ui_runner = UiTestRunner(config, parallel=args.parallel, tags=args.tags, submodule=submodule)
                ui_results = ui_runner.run()
                results.extend(ui_results)
                logger.info(f"UI子模块测试执行完成: {submodule}")
            elif module_type == "ssh":
                logger.info(f"开始执行SSH子模块测试: {submodule}")
                ssh_runner = SshTestRunner(config, parallel=args.parallel, tags=args.tags, submodule=submodule)
                ssh_results = ssh_runner.run()
                results.extend(ssh_results)
                logger.info(f"SSH子模块测试执行完成: {submodule}")
            else:
                logger.error(f"不支持的模块类型: {module_type}")
                return 1
        else:
            # 否则，根据 --module 参数运行测试
            if args.module in ["api", "all"]:
                logger.info("开始执行API测试")
                api_runner = ApiTestRunner(config, parallel=args.parallel, tags=args.tags)
                api_results = api_runner.run()
                results.extend(api_results)
                logger.info("API测试执行完成")
            
            if args.module in ["ui", "all"]:
                logger.info("开始执行UI测试")
                ui_runner = UiTestRunner(config, parallel=args.parallel, tags=args.tags)
                ui_results = ui_runner.run()
                results.extend(ui_results)
                logger.info("UI测试执行完成")
            
            if args.module in ["ssh", "all"]:
                logger.info("开始执行SSH测试")
                ssh_runner = SshTestRunner(config, parallel=args.parallel, tags=args.tags)
                ssh_results = ssh_runner.run()
                results.extend(ssh_results)
                logger.info("SSH测试执行完成")
        
        # 生成报告时使用Docker中的路径
        report_path = report_generator.generate(results)
        logger.info(f"测试报告已生成: {report_path}")
        
        # 确保报告目录权限正确
        if os.path.exists(report_path):
            os.chmod(report_path, 0o644)
        
        # 统计测试结果
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        
        logger.info(f"测试结果统计: 总计 {total}, 通过 {passed}, 失败 {failed}, 跳过 {skipped}")
        
        return 1 if failed > 0 else 0
    
    except Exception as e:
        logger.error(f"测试执行过程中发生错误: {str(e)}")
        return 1


if __name__ == "__main__":
    # 如果是作为Web应用运行
    if os.getenv('FLASK_APP'):
        from web_admin import app
        env_config = get_env_config()
        app.run(
            host=env_config['HOST'],
            port=env_config['PORT'],
            debug=env_config['FLASK_ENV'] == 'development'
        )
    else:
        # 如果是作为命令行工具运行
        exit_code = main()
        sys.exit(exit_code) 