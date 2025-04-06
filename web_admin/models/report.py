#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import glob
from datetime import datetime

# 报告数据文件路径
REPORT_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'reports.json')

# 确保数据目录存在
os.makedirs(os.path.dirname(REPORT_DATA_FILE), exist_ok=True)

class Report:
    """测试报告模型"""
    
    def __init__(self, id, name, path, type, task_id=None, created_at=None, summary=None):
        self.id = id
        self.name = name
        self.path = path
        self.type = type  # html, allure, json
        self.task_id = task_id
        self.created_at = created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.summary = summary or {}
    
    def to_dict(self):
        """将报告对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'type': self.type,
            'task_id': self.task_id,
            'created_at': self.created_at,
            'summary': self.summary
        }
    
    @staticmethod
    def get_all_reports():
        """获取所有报告"""
        if not os.path.exists(REPORT_DATA_FILE):
            return []
        
        try:
            with open(REPORT_DATA_FILE, 'r', encoding='utf-8') as f:
                reports_data = json.load(f)
                return [Report(**report_data) for report_data in reports_data]
        except Exception as e:
            print(f"读取报告数据失败: {str(e)}")
            return []
    
    @staticmethod
    def get_report_by_id(report_id):
        """根据ID获取报告"""
        reports = Report.get_all_reports()
        for report in reports:
            if report.id == report_id:
                return report
        return None
    
    @staticmethod
    def get_reports_by_task_id(task_id):
        """根据任务ID获取报告"""
        reports = Report.get_all_reports()
        return [report for report in reports if report.task_id == task_id]
    
    @staticmethod
    def add_report(name, path, type, task_id=None, summary=None):
        """添加新报告"""
        # 获取所有报告
        reports = Report.get_all_reports()
        
        # 生成新报告ID
        new_id = str(len(reports) + 1)
        
        # 创建新报告
        new_report = Report(
            id=new_id,
            name=name,
            path=path,
            type=type,
            task_id=task_id,
            summary=summary
        )
        
        # 添加到报告列表
        reports.append(new_report)
        
        # 保存报告数据
        try:
            with open(REPORT_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([report.to_dict() for report in reports], f, ensure_ascii=False, indent=2)
            return True, new_report
        except Exception as e:
            print(f"保存报告数据失败: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def delete_report(report_id):
        """删除报告"""
        reports = Report.get_all_reports()
        report_to_delete = None
        
        for report in reports:
            if report.id == report_id:
                report_to_delete = report
                break
        
        if report_to_delete:
            # 从列表中移除
            reports = [report for report in reports if report.id != report_id]
            
            # 保存报告数据
            try:
                with open(REPORT_DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump([report.to_dict() for report in reports], f, ensure_ascii=False, indent=2)
                
                # 尝试删除报告文件
                try:
                    if os.path.exists(report_to_delete.path):
                        os.remove(report_to_delete.path)
                except:
                    pass
                
                return True, "报告删除成功"
            except Exception as e:
                print(f"保存报告数据失败: {str(e)}")
                return False, str(e)
        
        return False, "报告不存在"
    
    @staticmethod
    def scan_reports_directory():
        """扫描报告目录，添加新报告"""
        # 报告目录
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        reports_dir = os.path.join(base_dir, 'reports')
        
        if not os.path.exists(reports_dir):
            return False, "报告目录不存在"
        
        # 获取所有报告文件
        html_reports = glob.glob(os.path.join(reports_dir, 'report_*.html'))
        json_reports = glob.glob(os.path.join(reports_dir, 'report_*.json'))
        allure_reports = glob.glob(os.path.join(reports_dir, 'allure_report_*'))
        
        # 获取已有报告路径
        existing_reports = Report.get_all_reports()
        existing_paths = [report.path for report in existing_reports]
        
        # 添加新报告
        new_reports = []
        
        # 处理HTML报告
        for report_path in html_reports:
            if report_path not in existing_paths:
                report_name = os.path.basename(report_path)
                success, report = Report.add_report(
                    name=report_name,
                    path=report_path,
                    type='html'
                )
                if success:
                    new_reports.append(report)
        
        # 处理JSON报告
        for report_path in json_reports:
            if report_path not in existing_paths:
                report_name = os.path.basename(report_path)
                success, report = Report.add_report(
                    name=report_name,
                    path=report_path,
                    type='json'
                )
                if success:
                    new_reports.append(report)
        
        # 处理Allure报告
        for report_path in allure_reports:
            if report_path not in existing_paths:
                report_name = os.path.basename(report_path)
                success, report = Report.add_report(
                    name=report_name,
                    path=report_path,
                    type='allure'
                )
                if success:
                    new_reports.append(report)
        
        return True, new_reports 