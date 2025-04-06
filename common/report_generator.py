#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import shutil
from datetime import datetime
from loguru import logger


class ReportGenerator:
    """报告生成器，用于生成不同格式的测试报告"""
    
    def __init__(self, report_type="html"):
        """
        初始化报告生成器
        
        Args:
            report_type: 报告类型，可选值为 html, allure, json
        """
        self.report_type = report_type
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.report_dir = os.path.join(self.base_dir, "reports")
        
        # 确保报告目录存在
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
    
    def generate(self, results):
        """
        生成测试报告
        
        Args:
            results: 测试结果列表
            
        Returns:
            生成的报告路径
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        if self.report_type == "html":
            return self._generate_html_report(results, timestamp)
        elif self.report_type == "allure":
            return self._generate_allure_report(results, timestamp)
        elif self.report_type == "json":
            return self._generate_json_report(results, timestamp)
        else:
            logger.warning(f"不支持的报告类型: {self.report_type}，将使用HTML格式")
            return self._generate_html_report(results, timestamp)
    
    def _generate_html_report(self, results, timestamp):
        """生成HTML格式的测试报告"""
        report_path = os.path.join(self.report_dir, f"report_{timestamp}.html")
        
        # 统计测试结果
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        
        # 计算通过率
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # 生成HTML报告
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>自动化测试报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1, h2 {{
            color: #333;
        }}
        .summary {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }}
        .summary-item {{
            text-align: center;
            padding: 15px;
            border-radius: 5px;
            flex: 1;
            margin: 0 10px;
            color: white;
        }}
        .total {{
            background-color: #2196F3;
        }}
        .passed {{
            background-color: #4CAF50;
        }}
        .failed {{
            background-color: #F44336;
        }}
        .skipped {{
            background-color: #FF9800;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .status-passed {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .status-failed {{
            color: #F44336;
            font-weight: bold;
        }}
        .status-skipped {{
            color: #FF9800;
            font-weight: bold;
        }}
        .details {{
            margin-top: 10px;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 5px;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>自动化测试报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <div class="summary-item total">
                <h2>总计</h2>
                <p>{total}</p>
            </div>
            <div class="summary-item passed">
                <h2>通过</h2>
                <p>{passed}</p>
            </div>
            <div class="summary-item failed">
                <h2>失败</h2>
                <p>{failed}</p>
            </div>
            <div class="summary-item skipped">
                <h2>跳过</h2>
                <p>{skipped}</p>
            </div>
        </div>
        
        <h2>通过率: {pass_rate:.2f}%</h2>
        
        <h2>测试详情</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>模块</th>
                <th>名称</th>
                <th>状态</th>
                <th>耗时(秒)</th>
            </tr>
""")
            
            # 添加测试结果行
            for i, result in enumerate(results):
                status_class = f"status-{result.get('status', '')}"
                f.write(f"""
            <tr>
                <td>{i+1}</td>
                <td>{result.get('module', '')}</td>
                <td>{result.get('name', '')}</td>
                <td class="{status_class}">{result.get('status', '')}</td>
                <td>{result.get('duration', 0):.2f}</td>
            </tr>
            <tr>
                <td colspan="5">
                    <div class="details">
                        <strong>描述:</strong> {result.get('description', '')}<br>
                        <strong>开始时间:</strong> {result.get('start_time', '')}<br>
                        <strong>结束时间:</strong> {result.get('end_time', '')}<br>
                        {f"<strong>错误信息:</strong> {result.get('error', '')}" if result.get('error') else ''}
                    </div>
                </td>
            </tr>
""")
            
            f.write("""
        </table>
    </div>
</body>
</html>
""")
        
        logger.info(f"HTML报告已生成: {report_path}")
        return report_path
    
    def _generate_allure_report(self, results, timestamp):
        """生成Allure格式的测试报告"""
        # 创建临时结果目录
        results_dir = os.path.join(self.report_dir, f"allure_results_{timestamp}")
        report_dir = os.path.join(self.report_dir, f"allure_report_{timestamp}")
        
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        # 为每个测试结果生成Allure JSON文件
        for i, result in enumerate(results):
            result_file = os.path.join(results_dir, f"result_{i+1}.json")
            
            allure_result = {
                "name": result.get("name", ""),
                "status": result.get("status", ""),
                "statusDetails": {
                    "message": result.get("error", "") if result.get("status") == "failed" else "",
                    "trace": result.get("traceback", "") if result.get("status") == "failed" else ""
                },
                "stage": "finished",
                "description": result.get("description", ""),
                "start": result.get("start_timestamp", 0),
                "stop": result.get("end_timestamp", 0),
                "labels": [
                    {"name": "suite", "value": result.get("module", "")}
                ]
            }
            
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(allure_result, f, ensure_ascii=False, indent=2)
        
        # 尝试使用allure命令生成报告
        try:
            import subprocess
            subprocess.run(["allure", "generate", results_dir, "-o", report_dir, "--clean"], check=True)
            logger.info(f"Allure报告已生成: {report_dir}")
            return report_dir
        except Exception as e:
            logger.error(f"生成Allure报告失败: {str(e)}")
            logger.info(f"Allure结果文件已保存在: {results_dir}")
            return results_dir
    
    def _generate_json_report(self, results, timestamp):
        """生成JSON格式的测试报告"""
        report_path = os.path.join(self.report_dir, f"report_{timestamp}.json")
        
        # 统计测试结果
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        
        # 计算通过率
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # 生成报告数据
        report_data = {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "pass_rate": pass_rate
            },
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": results
        }
        
        # 写入JSON文件
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON报告已生成: {report_path}")
        return report_path 