#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务计划调度工具
作者: longshen
"""

import os
import json
import time
import threading
import logging
from datetime import datetime
import platform

# 确保日志目录存在
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'scheduler.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('scheduler')

# 尝试导入schedule，如果失败则创建一个模拟的schedule
try:
    import schedule
    # 检查是否缺少必要的函数
    if not hasattr(schedule, 'clear') or not hasattr(schedule, 'run_pending'):
        # 创建兼容层
        class ScheduleCompat:
            def __init__(self):
                self.jobs = {}
                
            def clear(self, tag=None):
                if tag:
                    if tag in self.jobs:
                        del self.jobs[tag]
                else:
                    self.jobs.clear()
                
            def run_pending(self):
                # 简单实现，实际应用中会更复杂
                pass
                
            def every(self, interval=1):
                # 简单实现，实际应用中会更复杂
                class Job:
                    def at(self, time_str):
                        return self
                    def do(self, job_func, *args, **kwargs):
                        return self
                    def tag(self, tag_name):
                        return self
                return Job()
                
        # 替换全局schedule
        schedule = ScheduleCompat()
except ImportError:
    # 创建一个模拟的schedule
    class ScheduleMock:
        def __init__(self):
            self.jobs = {}
            
        def clear(self, tag=None):
            if tag:
                if tag in self.jobs:
                    del self.jobs[tag]
            else:
                self.jobs.clear()
            
        def run_pending(self):
            # 简单实现，实际应用中会更复杂
            pass
            
        def every(self, interval=1):
            # 简单实现，实际应用中会更复杂
            class Job:
                def at(self, time_str):
                    return self
                def do(self, job_func, *args, **kwargs):
                    return self
                def tag(self, tag_name):
                    return self
            return Job()
            
    schedule = ScheduleMock()
    logging.warning("无法导入schedule库，使用模拟实现")

class TaskScheduler:
    """
    任务调度器类
    用于管理和执行定时任务
    """
    
    def __init__(self, tasks_file='scheduled_tasks.json', data_dir=None):
        """
        初始化任务调度器
        
        参数:
            tasks_file: 任务配置文件名
            data_dir: 数据目录
        """
        # 使用绝对路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = data_dir if data_dir else os.path.join(base_dir, 'data')
        self.tasks_file = os.path.join(self.data_dir, tasks_file)
        self.tasks = {}
        self.running = False
        self.thread = None
        
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        logger.info(f"数据目录: {self.data_dir}")
        logger.info(f"任务文件: {self.tasks_file}")
        
        # 加载已有任务
        self.load_tasks()
    
    def load_tasks(self):
        """加载任务配置"""
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                
                # 注册所有任务到调度器
                self._register_all_tasks()
                logger.info(f"已加载 {len(self.tasks)} 个任务")
            else:
                logger.info("任务配置文件不存在，将创建新文件")
                self.save_tasks()
        except Exception as e:
            logger.error(f"加载任务失败: {str(e)}")
            self.tasks = {}
    
    def save_tasks(self):
        """保存任务配置"""
        try:
            # 确保父目录存在
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            logger.info("任务配置已保存")
        except Exception as e:
            logger.error(f"保存任务失败: {str(e)}")
    
    def add_task(self, task_id, name, command, schedule_type, schedule_value, 
                 description="", enabled=True, notify=False, notify_config=None):
        """
        添加新任务
        
        参数:
            task_id: 任务ID
            name: 任务名称
            command: 要执行的命令
            schedule_type: 调度类型 (daily, weekly, monthly, interval)
            schedule_value: 调度值 (取决于类型，例如："12:00", "Monday 12:00", "1 12:00", "3600")
            description: 任务描述
            enabled: 是否启用
            notify: 是否通知
            notify_config: 通知配置
        
        返回:
            成功返回True，否则返回False
        """
        try:
            # 生成任务ID（如果未提供）
            if not task_id:
                task_id = f"task_{int(time.time())}"
            
            # 创建任务
            task = {
                "id": task_id,
                "name": name,
                "command": command,
                "schedule_type": schedule_type,
                "schedule_value": schedule_value,
                "description": description,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_run": None,
                "enabled": enabled,
                "notify": notify,
                "notify_config": notify_config or {}
            }
            
            # 添加到任务列表
            self.tasks[task_id] = task
            
            # 如果任务启用，注册到调度器
            if enabled:
                self._register_task(task)
            
            # 保存任务
            self.save_tasks()
            logger.info(f"添加任务成功: {name} (ID: {task_id})")
            return True
        except Exception as e:
            logger.error(f"添加任务失败: {str(e)}")
            return False
    
    def update_task(self, task_id, **kwargs):
        """
        更新现有任务
        
        参数:
            task_id: 要更新的任务ID
            **kwargs: 要更新的任务属性
        
        返回:
            成功返回True，否则返回False
        """
        try:
            if task_id not in self.tasks:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            # 取消现有任务的调度
            schedule.clear(task_id)
            
            # 更新任务属性
            for key, value in kwargs.items():
                if key in self.tasks[task_id]:
                    self.tasks[task_id][key] = value
            
            # 如果任务启用，重新注册到调度器
            if self.tasks[task_id]["enabled"]:
                self._register_task(self.tasks[task_id])
            
            # 保存任务
            self.save_tasks()
            logger.info(f"更新任务成功: {self.tasks[task_id]['name']} (ID: {task_id})")
            return True
        except Exception as e:
            logger.error(f"更新任务失败: {str(e)}")
            return False
    
    def delete_task(self, task_id):
        """
        删除任务
        
        参数:
            task_id: 要删除的任务ID
        
        返回:
            成功返回True，否则返回False
        """
        try:
            if task_id not in self.tasks:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            # 取消任务的调度
            schedule.clear(task_id)
            
            # 从任务列表中删除
            task_name = self.tasks[task_id]['name']
            del self.tasks[task_id]
            
            # 保存任务
            self.save_tasks()
            logger.info(f"删除任务成功: {task_name} (ID: {task_id})")
            return True
        except Exception as e:
            logger.error(f"删除任务失败: {str(e)}")
            return False
    
    def enable_task(self, task_id, enabled=True):
        """
        启用或禁用任务
        
        参数:
            task_id: 任务ID
            enabled: 是否启用
        
        返回:
            成功返回True，否则返回False
        """
        try:
            if task_id not in self.tasks:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            # 更新任务状态
            self.tasks[task_id]['enabled'] = enabled
            
            # 根据状态处理调度
            if enabled:
                self._register_task(self.tasks[task_id])
                logger.info(f"已启用任务: {self.tasks[task_id]['name']} (ID: {task_id})")
            else:
                schedule.clear(task_id)
                logger.info(f"已禁用任务: {self.tasks[task_id]['name']} (ID: {task_id})")
            
            # 保存任务
            self.save_tasks()
            return True
        except Exception as e:
            logger.error(f"更新任务状态失败: {str(e)}")
            return False
    
    def get_task(self, task_id):
        """
        获取任务详情
        
        参数:
            task_id: 任务ID
        
        返回:
            任务详情或None
        """
        return self.tasks.get(task_id)
    
    def get_all_tasks(self):
        """
        获取所有任务
        
        返回:
            任务列表
        """
        return list(self.tasks.values())
    
    def start(self):
        """
        启动调度器
        """
        if self.running:
            logger.warning("调度器已经在运行中")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._run_continuously)
        self.thread.daemon = True
        self.thread.start()
        logger.info("调度器已启动")
        return True
    
    def stop(self):
        """
        停止调度器
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=3)
        logger.info("调度器已停止")
    
    def _run_continuously(self):
        """持续运行调度器"""
        while self.running:
            try:
                schedule.run_pending()
            except Exception as e:
                logger.error(f"执行调度任务时出错: {str(e)}")
            time.sleep(1)
    
    def _register_all_tasks(self):
        """
        注册所有启用的任务到调度器
        """
        for task_id, task in self.tasks.items():
            if task['enabled']:
                self._register_task(task)
    
    def _register_task(self, task):
        """
        注册单个任务到调度器
        
        参数:
            task: 任务详情
        """
        try:
            task_id = task['id']
            schedule_type = task['schedule_type']
            schedule_value = task['schedule_value']
            
            # 清除可能已存在的任务
            schedule.clear(task_id)
            
            # 创建任务执行函数
            def job_func():
                self._execute_task(task_id)
            
            # 根据调度类型设置调度
            job = None
            
            if schedule_type == 'daily':
                # 每天执行，格式: "HH:MM"
                job = schedule.every().day.at(schedule_value)
            elif schedule_type == 'weekly':
                # 每周执行，格式: "Monday 12:00"
                day, time_str = schedule_value.split(' ', 1)
                job = getattr(schedule.every(), day.lower()).at(time_str)
            elif schedule_type == 'monthly':
                # 每月执行，格式: "1 12:00"（每月1号12:00）
                day, time_str = schedule_value.split(' ', 1)
                
                # 使用自定义处理逻辑检查月份日期
                def monthly_job():
                    current_day = datetime.now().day
                    if current_day == int(day):
                        target_time = datetime.strptime(time_str, "%H:%M").time()
                        current_time = datetime.now().time()
                        # 如果当前时间在目标时间之前，返回目标时间和当前时间的秒数差
                        if current_time.hour < target_time.hour or (current_time.hour == target_time.hour and current_time.minute < target_time.minute):
                            target_dt = datetime.combine(datetime.now().date(), target_time)
                            current_dt = datetime.combine(datetime.now().date(), current_time)
                            seconds_diff = (target_dt - current_dt).total_seconds()
                            return seconds_diff
                    return -1  # 不执行
                
                # 检查执行条件并添加调度
                job = schedule.every().day.do(monthly_job)
            elif schedule_type == 'interval':
                # 间隔执行，格式: 秒数
                interval_seconds = int(schedule_value)
                job = schedule.every(interval_seconds).seconds
            else:
                logger.error(f"不支持的调度类型: {schedule_type}")
                return
            
            # 添加任务
            job.do(job_func).tag(task_id)
            logger.info(f"已注册任务到调度器: {task['name']} (ID: {task_id})")
        except Exception as e:
            logger.error(f"注册任务失败: {str(e)}")
    
    def _execute_task(self, task_id):
        """
        执行任务
        
        参数:
            task_id: 任务ID
        """
        if task_id not in self.tasks:
            logger.error(f"任务不存在: {task_id}")
            return
        
        task = self.tasks[task_id]
        command = task['command']
        
        try:
            logger.info(f"执行任务: {task['name']} (ID: {task_id})")
            
            # 更新最后执行时间
            self.tasks[task_id]['last_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_tasks()
            
            # 执行命令
            start_time = time.time()
            is_windows = platform.system().lower() == 'windows'
            
            if is_windows:
                import subprocess
                process = subprocess.Popen(command, shell=True)
                return_code = process.wait()
            else:
                return_code = os.system(command)
            
            duration = time.time() - start_time
            
            # 记录执行结果
            if return_code == 0:
                logger.info(f"任务执行成功: {task['name']} (ID: {task_id}), 耗时: {duration:.2f}秒")
                
                # 发送通知（如果启用）
                if task.get('notify') and task.get('notify_config'):
                    self._send_notification(task, True, duration)
            else:
                logger.error(f"任务执行失败: {task['name']} (ID: {task_id}), 状态码: {return_code}, 耗时: {duration:.2f}秒")
                
                # 发送通知（如果启用）
                if task.get('notify') and task.get('notify_config'):
                    self._send_notification(task, False, duration, return_code)
        except Exception as e:
            logger.error(f"执行任务时出错: {task['name']} (ID: {task_id}), 错误: {str(e)}")
            
            # 发送通知（如果启用）
            if task.get('notify') and task.get('notify_config'):
                self._send_notification(task, False, 0, str(e))
    
    def _send_notification(self, task, success, duration, error=None):
        """
        发送任务执行通知
        
        参数:
            task: 任务详情
            success: 是否成功
            duration: 执行时间（秒）
            error: 错误信息（如果有）
        """
        try:
            notify_type = task.get('notify_config', {}).get('type', 'dingtalk')
            
            if notify_type == 'dingtalk':
                self._send_dingtalk_notification(task, success, duration, error)
            else:
                logger.warning(f"不支持的通知类型: {notify_type}")
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")
    
    def _send_dingtalk_notification(self, task, success, duration, error=None):
        """
        发送钉钉通知
        
        参数:
            task: 任务详情
            success: 是否成功
            duration: 执行时间（秒）
            error: 错误信息（如果有）
        """
        try:
            from .dingtalk import DingTalkNotifier
            
            notify_config = task.get('notify_config', {})
            webhook_url = notify_config.get('webhook_url')
            secret = notify_config.get('secret')
            
            if not webhook_url:
                logger.error("钉钉通知失败: 缺少webhook URL")
                return
            
            # 创建钉钉通知器
            notifier = DingTalkNotifier(webhook_url, secret)
            
            # 构建通知内容
            status = "成功" if success else "失败"
            status_emoji = "✅" if success else "❌"
            
            title = f"定时任务执行{status}: {task['name']}"
            
            message = f"""## {status_emoji} 定时任务执行{status}: {task['name']}

### 📊 任务概况
- **任务ID**: {task['id']}
- **状态**: {status_emoji} {status}
- **执行时间**: {task['last_run']}
- **耗时**: {duration:.2f}秒

### 📋 任务命令
```
{task['command']}
```

"""
            
            # 添加错误信息（如果有）
            if not success and error:
                message += f"""### ❗ 错误信息
```
{error}
```

"""
            
            message += "> 本消息由自动化测试平台生成\n> 作者: longshen"
            
            # 发送通知
            response = notifier.send_markdown(title, message)
            
            if response.get('errcode') == 0:
                logger.info(f"钉钉通知发送成功: {task['name']} (ID: {task['id']})")
            else:
                logger.error(f"钉钉通知发送失败: {response.get('errmsg')}")
        except Exception as e:
            logger.error(f"发送钉钉通知失败: {str(e)}")


# 单例模式获取调度器实例
_scheduler_instance = None

def get_scheduler():
    """
    获取调度器实例（单例模式）
    
    返回:
        TaskScheduler实例
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = TaskScheduler()
    return _scheduler_instance


# 用法示例
if __name__ == "__main__":
    # 获取任务调度器实例
    scheduler = get_scheduler()
    
    # 添加示例任务
    # scheduler.add_task(
    #     task_id="daily_backup",
    #     name="每日备份",
    #     command="python backup.py",
    #     schedule_type="daily",
    #     schedule_value="03:00",
    #     description="执行每日备份任务",
    #     enabled=True
    # )
    
    # 启动调度器
    scheduler.start()
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        # 停止调度器
        scheduler.stop()
        print("调度器已停止") 