#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import uuid
import time
from datetime import datetime

# 任务数据文件路径
TASK_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tasks.json')

# 确保数据目录存在
os.makedirs(os.path.dirname(TASK_DATA_FILE), exist_ok=True)

class Task:
    """测试任务模型"""
    
    def __init__(self, id=None, name=None, modules=None, submodules=None, env='test', 
                 report_type='html', parallel=1, tags=None, status='pending', 
                 created_by=None, created_at=None, started_at=None, finished_at=None, 
                 report_path=None, result=None, error=None):
        self.id = id or str(uuid.uuid4())
        self.name = name or f"测试任务-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.modules = modules or []  # ['api', 'ui', 'ssh']
        self.submodules = submodules or []  # ['api.user', 'ui.login']
        self.env = env
        self.report_type = report_type
        self.parallel = parallel
        self.tags = tags
        self.status = status  # pending, running, completed, failed
        self.created_by = created_by
        self.created_at = created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.started_at = started_at
        self.finished_at = finished_at
        self.report_path = report_path
        self.result = result or {}
        self.error = error
    
    def to_dict(self):
        """将任务对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'modules': self.modules,
            'submodules': self.submodules,
            'env': self.env,
            'report_type': self.report_type,
            'parallel': self.parallel,
            'tags': self.tags,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'finished_at': self.finished_at,
            'report_path': self.report_path,
            'result': self.result,
            'error': self.error
        }
    
    @staticmethod
    def get_all_tasks():
        """获取所有任务"""
        if not os.path.exists(TASK_DATA_FILE):
            return []
        
        try:
            with open(TASK_DATA_FILE, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
                return [Task(**task_data) for task_data in tasks_data]
        except Exception as e:
            print(f"读取任务数据失败: {str(e)}")
            return []
    
    @staticmethod
    def get_task_by_id(task_id):
        """根据ID获取任务"""
        tasks = Task.get_all_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None
    
    @staticmethod
    def create_task(name, modules, submodules=None, env='test', report_type='html', 
                    parallel=1, tags=None, created_by=None):
        """创建新任务"""
        # 获取所有任务
        tasks = Task.get_all_tasks()
        
        # 创建新任务
        new_task = Task(
            name=name,
            modules=modules,
            submodules=submodules or [],
            env=env,
            report_type=report_type,
            parallel=parallel,
            tags=tags,
            created_by=created_by
        )
        
        # 添加到任务列表
        tasks.append(new_task)
        
        # 保存任务数据
        try:
            with open(TASK_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([task.to_dict() for task in tasks], f, ensure_ascii=False, indent=2)
            return True, new_task
        except Exception as e:
            print(f"保存任务数据失败: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def update_task(task_id, **kwargs):
        """更新任务信息"""
        tasks = Task.get_all_tasks()
        updated = False
        
        for i, task in enumerate(tasks):
            if task.id == task_id:
                # 更新任务信息
                for key, value in kwargs.items():
                    setattr(task, key, value)
                
                tasks[i] = task
                updated = True
                break
        
        if updated:
            # 保存任务数据
            try:
                with open(TASK_DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump([task.to_dict() for task in tasks], f, ensure_ascii=False, indent=2)
                return True, "任务信息更新成功"
            except Exception as e:
                print(f"保存任务数据失败: {str(e)}")
                return False, str(e)
        
        return False, "任务不存在"
    
    @staticmethod
    def delete_task(task_id):
        """删除任务"""
        tasks = Task.get_all_tasks()
        tasks = [task for task in tasks if task.id != task_id]
        
        # 保存任务数据
        try:
            with open(TASK_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([task.to_dict() for task in tasks], f, ensure_ascii=False, indent=2)
            return True, "任务删除成功"
        except Exception as e:
            print(f"保存任务数据失败: {str(e)}")
            return False, str(e) 