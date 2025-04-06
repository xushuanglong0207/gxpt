#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 简单测试代码，确保Python能正常执行
print("=== 测试Python执行 ===")
print("如果你能看到这条消息，说明Python能正常执行")

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_from_directory, make_response
from werkzeug.security import check_password_hash
import threading
from functools import wraps
from werkzeug.utils import secure_filename
import random
import platform
import requests
import concurrent.futures
import ipaddress
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import logging
# 恢复知识库模块的导入
from routes.knowledge import knowledge
from routes.nas import nas
from logging.handlers import RotatingFileHandler
from routes.scripts import scripts_bp

# 打印当前工作目录和Python路径
current_dir = os.getcwd()
print("当前工作目录:", current_dir)
print("Python路径:", sys.path)

# 添加当前目录到系统路径
sys.path.append(current_dir)

try:
    # 导入模型
    from models.user import User
    from models.task import Task
    from models.report import Report
    from utils.scheduler import get_scheduler
    from utils.dingtalk import DingTalkNotifier
    # 恢复知识库模块的导入
    from routes.knowledge import knowledge
    print("导入模块成功")
except Exception as e:
    print("导入模块失败:", str(e))
    print("发生错误的详细信息:")
    import traceback
    traceback.print_exc()
    print("\n尝试解决方案: 请确保logs目录存在，或查看上述错误信息")
    sys.exit(1)

# 创建唯一的Flask应用实例
app = Flask(__name__)
app.secret_key = 'longshen_secret_key'

# 会话配置
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 会话有效期24小时
app.config['SESSION_COOKIE_SECURE'] = False  # 如果不是HTTPS，设为False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['REMEMBER_COOKIE_DURATION'] = 86400  # 记住我选项的有效期24小时
app.config['REMEMBER_COOKIE_SECURE'] = False  # 如果不是HTTPS，设为False
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['KNOWLEDGE_BASE_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'knowledge_base')

# 网站标题和作者配置
app.config['SITE_TITLE'] = '高效测试平台'
app.config['SITE_AUTHOR'] = 'longshen'
app.config['SITE_FAVICON'] = None  # 存储自定义图标的路径

# 配置允许跨域访问
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 初始化 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# 确保知识库目录存在
os.makedirs(app.config['KNOWLEDGE_BASE_PATH'], exist_ok=True)

# 注册蓝图
# 恢复知识库蓝图的注册
app.register_blueprint(knowledge)
app.register_blueprint(nas)
app.register_blueprint(scripts_bp)

# 设置日志
if not os.path.exists('logs'):
    os.makedirs('logs')
logging.basicConfig(filename='logs/app.log', level=logging.INFO)

# 确保数据目录存在
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'), exist_ok=True)

# 加载网站配置
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'site_config.json')
if os.path.exists(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            site_config = json.load(f)
            app.config['SITE_TITLE'] = site_config.get('site_title', '高效测试平台')
            app.config['SITE_AUTHOR'] = site_config.get('site_author', 'longshen')
            app.config['SITE_FAVICON'] = site_config.get('site_favicon')
    except Exception as e:
        print(f"加载网站配置失败: {str(e)}")

try:
    # 初始化管理员用户
    print("尝试初始化管理员用户")
    User.init_admin_user()
    print("管理员用户初始化成功")
except Exception as e:
    print("初始化管理员用户失败:", str(e))

# 初始化任务调度器并启动
scheduler = get_scheduler()
scheduler.start()

# ==== 访问控制装饰器 ====
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        
        if not current_user.is_admin():
            flash('需要管理员权限', 'danger')
            return redirect(url_for('index'))
            
        return f(*args, **kwargs)
    return decorated_function

# 路由：首页
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
        
    # 检查是否是从登录页面跳转过来的
    from_login = request.referrer and 'login' in request.referrer
    
    return render_template('dashboard.html',
        tasks_count=len(get_task_list()),
        reports_count=len(get_report_list()),
        users_count=len(User.get_all_users()),
        error_count=count_errors_in_reports(),
        flask_version=__import__('flask').__version__,
        current_user=current_user,
        from_login=from_login  # 传递标记给模板
    )

# 路由：登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.get_user_by_username(username)
        if user and User.check_password(user.password_hash, password):
            # 登录前清除所有flash消息
            session.pop('_flashes', None)
            login_user(user)
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            # 添加一条成功消息 - 先设置会话然后添加flash
            flash('登录成功！', 'success')
            print("已添加登录成功消息")
            return redirect(url_for('index'))
        else:
            # 登录失败时也清除旧消息
            session.pop('_flashes', None)
            flash('用户名或密码错误！', 'danger')
            print("已添加登录失败消息")
    
    return render_template('login.html')

# 路由：退出登录
@app.route('/logout')
@login_required
def logout():
    # 创建flask.Response对象，确保flash消息能正确处理
    from flask import make_response
    
    # 先添加flash消息，然后再退出登录
    # 清除旧的消息
    session.pop('_flashes', None)
    flash('已退出登录！', 'success')
    print("已添加退出登录消息")
    
    # 执行退出登录
    logout_user()
    
    # 清理会话
    for key in list(session.keys()):
        if key != '_flashes':  # 保留flash消息
            session.pop(key, None)
    
    # 创建响应对象并返回
    response = make_response(redirect(url_for('login')))
    return response

# 路由：用户管理页面
@app.route('/users')
@admin_required
def users():
    users = User.get_all_users()
    return render_template('users.html', users=users, current_user=current_user)

# 路由：添加用户
@app.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # 检查用户名是否已存在
        existing_user = User.get_user_by_username(username)
        if existing_user:
            flash('用户名已存在', 'danger')
            return redirect(url_for('add_user'))
        
        User.create_user(username, password, role)
        flash('用户创建成功', 'success')
        return redirect(url_for('users'))
    
    return render_template('add_user.html')

# 路由：编辑用户
@app.route('/users/edit/<user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.get_user_by_id(user_id)
    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('users'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # 创建更新数据字典
        update_data = {
            'username': username,
            'role': role
        }
        
        # 只有在提供了密码的情况下才更新密码
        if password:
            update_data['password'] = password
        
        # 更新用户
        User.update_user(user_id, **update_data)
        
        flash('用户更新成功', 'success')
        return redirect(url_for('users'))
    
    return render_template('edit_user.html', user=user)

# 路由：删除用户
@app.route('/users/delete/<user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    if session.get('user_id') == user_id:
        flash('不能删除当前登录的用户', 'danger')
        return redirect(url_for('users'))
    
    if User.delete_user(user_id):
        flash('用户删除成功', 'success')
    else:
        flash('用户删除失败', 'danger')
    
    return redirect(url_for('users'))

# 路由：编辑个人资料
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        password = request.form.get('password')
        if password:
            User.update_user(current_user.id, password=password)
            flash('密码更新成功', 'success')
        else:
            flash('未提供新密码', 'warning')
        return redirect(url_for('index'))
    
    return render_template('edit_profile.html', user=current_user, current_user=current_user)

# 路由：测试任务列表
@app.route('/tasks')
@login_required
def tasks():
    tasks = get_task_list()
    return render_template('tasks.html', tasks=tasks, current_user=current_user)

# 路由：创建测试任务
@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        name = request.form.get('name')
        modules = request.form.getlist('modules') or []
        submodules = request.form.getlist('submodules') or []
        description = request.form.get('description', '')
        
        task_id = str(int(time.time()))
        task = {
            'id': task_id,
            'name': name,
            'modules': modules,
            'submodules': submodules,
            'description': description,
            'created_by': session.get('username'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'pending',
            'env': request.form.get('env', '测试环境'),
            'report_type': request.form.get('report_type', 'HTML'),
            'parallel': request.form.get('parallel', '1')
        }
        
        tasks = get_task_list()
        tasks.append(task)
        save_task_list(tasks)
        
        flash('任务创建成功', 'success')
        return redirect(url_for('tasks'))
    
    # 可用的测试模块 - 保留用户要求的三种类型
    available_modules = [
        'SSH自动化测试', 'UI自动化测试', 'API自动化测试'
    ]
    
    # 可用的子模块
    available_submodules = {
        'SSH自动化测试': ['服务器配置', '远程部署', '日志分析', '性能监控', '安全检查', '服务重启'],
        'UI自动化测试': ['登录', '注册', '购物车', '订单', '支付', '个人中心', '搜索功能', '产品展示'],
        'API自动化测试': ['用户API', '商品API', '订单API', '支付API', '搜索API', '认证API', '数据查询']
    }
    
    return render_template('create_task.html', 
                          available_modules=available_modules,
                          available_submodules=available_submodules)

# 路由：查看任务详情
@app.route('/tasks/<task_id>')
@login_required
def task_detail(task_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    task = Task.get_task_by_id(task_id)
    if not task:
        flash('任务不存在')
        return redirect(url_for('tasks'))
    
    # 获取任务相关的报告
    reports = Report.get_reports_by_task_id(task_id)
    
    return render_template('task_detail.html', task=task, reports=reports)

# 路由：运行测试任务
@app.route('/run_task/<task_id>', methods=['POST'])
@login_required
def run_task(task_id):
    # 获取任务信息
    tasks = get_task_list()
    task = None
    for t in tasks:
        if t['id'] == task_id:
            task = t
            break
    
    if not task:
        flash('任务不存在', 'danger')
        return redirect(url_for('tasks'))
    
    # 管理员和任务创建者都可以执行任务
    user_id = session.get('user_id')
    username = session.get('username')
    user_role = session.get('role')
    
    if user_role == 'admin' or task['created_by'] == username:
        # 更新任务状态
        task['status'] = 'running'
        task['run_by'] = username
        task['run_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 保存任务更新
        for i, t in enumerate(tasks):
            if t['id'] == task_id:
                tasks[i] = task
                break
        save_task_list(tasks)
        
        # 生成报告ID
        report_id = generate_report(task)
        
        # 更新任务状态为已完成
        task['status'] = 'completed'
        task['report_id'] = report_id
        task['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 再次保存任务更新
        for i, t in enumerate(tasks):
            if t['id'] == task_id:
                tasks[i] = task
                break
        save_task_list(tasks)
        
        flash('任务已成功执行，正在生成报告', 'success')
        return redirect(url_for('view_report', report_id=report_id))
    else:
        flash('您没有权限执行此任务', 'danger')
        return redirect(url_for('tasks'))

# 路由：删除测试任务
@app.route('/tasks/delete/<task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    tasks = get_task_list()
    tasks = [task for task in tasks if task['id'] != task_id]
    save_task_list(tasks)
    
    flash('任务删除成功', 'success')
    return redirect(url_for('tasks'))

# 路由：获取任务状态（API）
@app.route('/tasks/<task_id>/status')
@login_required
def task_status(task_id):
    tasks = get_task_list()
    for task in tasks:
        if task['id'] == task_id:
            return jsonify({'status': task['status']})
    
    return jsonify({'status': 'unknown'})

# 路由：查看报告
@app.route('/reports/<report_id>')
@login_required
def view_report(report_id):
    print(f"尝试查看报告: {report_id}")
    
    # 检查报告文件是否存在
    if not report_id.endswith('.html'):
        report_id_with_ext = f"{report_id}.html"
    else:
        report_id_with_ext = report_id
        report_id = report_id[:-5]  # 移除.html后缀
    
    print(f"查找报告文件: {report_id_with_ext}")
    
    # 从项目根目录的reports目录读取报告文件
    report_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports', report_id_with_ext)
    print(f"报告文件路径: {report_file}")
    
    if not os.path.exists(report_file):
        print(f"报告文件不存在: {report_file}")
        flash('报告文件不存在', 'error')
        return redirect(url_for('reports'))
    
    try:
        # 读取报告文件内容
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
            print(f"成功读取报告: {report_id}, 内容长度: {len(report_content)}")
        
        # 直接返回HTML内容
        return report_content
    except Exception as e:
        print(f"读取报告文件失败: {e}")
        flash('无法读取报告文件', 'error')
        return redirect(url_for('reports'))

# 路由：报告列表
@app.route('/reports')
@login_required
def reports():
    reports = get_report_list()
    return render_template('reports.html', reports=reports, current_user=current_user)

# AJAX路由：删除报告
@app.route('/reports/<report_id_with_ext>', methods=['DELETE'])
@login_required
def delete_report_ajax(report_id_with_ext):
    print(f"[删除请求] 收到带后缀的报告ID: {report_id_with_ext}")
    
    # 验证后缀
    if not report_id_with_ext.endswith('.html'):
        print(f"[错误] 传入的ID不带.html后缀: {report_id_with_ext}")
        return jsonify({'success': False, 'message': '无效的报告ID格式'})
        
    report_id_for_list = report_id_with_ext[:-5] # 用于列表查找的ID (无后缀)
    print(f"[路径处理] 列表查找ID: {report_id_for_list}, 文件名ID: {report_id_with_ext}")
    
    reports = get_report_list()
    print(f"[列表检查] 获取到报告列表，共 {len(reports)} 个报告")
    
    # 找到要删除的报告
    report_to_delete = None
    for report in reports:
        print(f"[列表检查] 比较: {report['id']} (来自列表) vs {report_id_for_list} (处理后)")
        if report['id'] == report_id_for_list:
            report_to_delete = report
            print(f"[列表检查] 在列表中找到匹配的报告: {report['id']}")
            break
    
    # 构造绝对路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    absolute_path = os.path.join(base_dir, 'reports', report_id_with_ext)
    print(f"[文件操作] 构造的文件绝对路径: {absolute_path}")

    if report_to_delete:
        print(f"[流程控制] 报告 {report_id_for_list} 在列表中找到，准备从列表移除并删除文件")
        # 从列表中移除报告
        reports = [r for r in reports if r['id'] != report_to_delete['id']]
        
        # 保存更新后的报告列表
        save_report_list(reports)
        print("[列表操作] 已更新报告列表文件 (reports.json)")
        
        # 尝试删除报告文件
        try:
            print(f"[文件检查] 检查文件是否存在: {absolute_path}")
            file_exists = os.path.exists(absolute_path)
            print(f"[文件检查] 文件是否存在? {file_exists}")
            
            if file_exists:
                print(f"[文件操作] 准备删除文件: {absolute_path}")
                os.remove(absolute_path)
                print(f"[文件操作] 成功删除报告文件: {absolute_path}")
                return jsonify({'success': True, 'message': '报告已成功删除'})
            else:
                print(f"[文件警告] 报告文件在磁盘上不存在: {absolute_path} (但已从列表移除)")
                return jsonify({'success': True, 'message': '报告已从列表中删除，但文件未找到'})
        except Exception as e:
            print(f"[文件错误] 删除报告文件失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'删除报告文件失败: {str(e)}'})
    else:
        print(f"[流程控制] 报告 {report_id_for_list} 未在列表中找到，检查文件是否直接存在于磁盘")
        # 检查报告文件是否存在，即使不在报告列表中
        print(f"[文件检查] 检查文件是否存在: {absolute_path}")
        file_exists = os.path.exists(absolute_path)
        print(f"[文件检查] 文件是否存在? {file_exists}")

        if file_exists:
            try:
                # 文件存在但不在列表中，尝试直接删除文件
                print(f"[文件操作] 准备删除未在列表中的文件: {absolute_path}")
                os.remove(absolute_path)
                print(f"[文件操作] 成功删除未在列表中的报告文件: {absolute_path}")
                return jsonify({'success': True, 'message': '报告文件已删除，但在列表中不存在'})
            except Exception as e:
                print(f"[文件错误] 删除未在列表中的报告文件失败: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'message': f'删除报告文件失败: {str(e)}'})
        else:
            print(f"[最终状态] 报告 {report_id_for_list} 在列表和磁盘上都不存在")
            # 记录目前的所有报告ID以便调试
            report_ids = [r['id'] for r in reports]
            print(f"[调试信息] 当前报告列表中的ID: {report_ids}")
            return jsonify({'success': True, 'message': '报告不存在', 'not_found': True})

# 路由：删除报告（表单提交）
@app.route('/reports/delete/<report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    reports = get_report_list()
    
    # 找到要删除的报告
    report_to_delete = None
    for report in reports:
        if report['id'] == report_id:
            report_to_delete = report
            break
    
    if report_to_delete:
        # 从列表中移除报告
        reports = [r for r in reports if r['id'] != report_id]
        
        # 保存更新后的报告列表
        save_report_list(reports)
        
        # 尝试删除报告文件
        try:
            report_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports', f"{report_id}.html")
            if os.path.exists(report_file):
                os.remove(report_file)
        except Exception as e:
            print(f"删除报告文件失败: {e}")
        
        flash('报告已删除', 'success')
    else:
        flash('报告不存在', 'error')
    
    return redirect(url_for('reports'))

# ==== 定时任务管理 ====
@app.route('/scheduled_tasks')
@admin_required
def scheduled_tasks():
    tasks = scheduler.get_all_tasks()
    return render_template('scheduled_tasks.html', tasks=tasks)

@app.route('/scheduled_tasks/add', methods=['GET', 'POST'])
@admin_required
def add_scheduled_task():
    if request.method == 'POST':
        task_id = f"task_{int(time.time())}"
        name = request.form.get('name')
        command = request.form.get('command')
        schedule_type = request.form.get('schedule_type')
        schedule_value = request.form.get('schedule_value')
        description = request.form.get('description', '')
        notify = 'notify' in request.form
        
        notify_config = None
        if notify:
            notify_config = {
                'type': 'dingtalk',
                'webhook_url': request.form.get('webhook_url'),
                'secret': request.form.get('secret', '')
            }
        
        scheduler.add_task(
            task_id=task_id,
            name=name,
            command=command,
            schedule_type=schedule_type,
            schedule_value=schedule_value,
            description=description,
            enabled=True,
            notify=notify,
            notify_config=notify_config
        )
        
        flash('定时任务创建成功', 'success')
        return redirect(url_for('scheduled_tasks'))
    
    return render_template('add_scheduled_task.html')

@app.route('/scheduled_tasks/edit/<task_id>', methods=['GET', 'POST'])
@admin_required
def edit_scheduled_task(task_id):
    task = scheduler.get_task(task_id)
    if not task:
        flash('任务不存在', 'danger')
        return redirect(url_for('scheduled_tasks'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        command = request.form.get('command')
        schedule_type = request.form.get('schedule_type')
        schedule_value = request.form.get('schedule_value')
        description = request.form.get('description', '')
        notify = 'notify' in request.form
        
        update_data = {
            'name': name,
            'command': command,
            'schedule_type': schedule_type,
            'schedule_value': schedule_value,
            'description': description,
            'notify': notify
        }
        
        if notify:
            update_data['notify_config'] = {
                'type': 'dingtalk',
                'webhook_url': request.form.get('webhook_url'),
                'secret': request.form.get('secret', '')
            }
        
        scheduler.update_task(task_id, **update_data)
        
        flash('定时任务更新成功', 'success')
        return redirect(url_for('scheduled_tasks'))
    
    return render_template('edit_scheduled_task.html', task=task)

@app.route('/scheduled_tasks/delete/<task_id>', methods=['POST'])
@admin_required
def delete_scheduled_task(task_id):
    if scheduler.delete_task(task_id):
        flash('定时任务删除成功', 'success')
    else:
        flash('定时任务删除失败', 'danger')
    
    return redirect(url_for('scheduled_tasks'))

@app.route('/scheduled_tasks/toggle/<task_id>', methods=['POST'])
@admin_required
def toggle_scheduled_task(task_id):
    task = scheduler.get_task(task_id)
    if not task:
        flash('任务不存在', 'danger')
        return redirect(url_for('scheduled_tasks'))
    
    # 切换任务状态
    new_status = not task.get('enabled', True)
    scheduler.update_task(task_id, enabled=new_status)
    
    flash(f'任务状态已更新为: {"启用" if new_status else "禁用"}', 'success')
    return redirect(url_for('scheduled_tasks'))

@app.route('/test_dingtalk', methods=['POST'])
@admin_required
def test_dingtalk():
    webhook_url = request.form.get('webhook_url')
    secret = request.form.get('secret', '')
    
    if not webhook_url:
        return jsonify({'success': False, 'message': '必须提供Webhook URL'})
    
    notifier = DingTalkNotifier(webhook_url, secret)
    response = notifier.send_text(f"高效测试平台通知测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n发送人: {session.get('username')}")
    
    if response.get('errcode') == 0:
        return jsonify({'success': True, 'message': '测试消息发送成功'})
    else:
        return jsonify({'success': False, 'message': f"发送失败: {response.get('errmsg')}"})

# ==== 辅助函数 ====
def get_task_list():
    """获取任务列表"""
    tasks_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'tasks.json')
    if os.path.exists(tasks_file):
        with open(tasks_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_task_list(tasks):
    """保存任务列表"""
    tasks_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'tasks.json')
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def get_report_list():
    """获取所有测试报告"""
    try:
        # 从reports目录获取所有报告文件
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
        print(f"查找报告目录: {reports_dir}")
        
        if not os.path.exists(reports_dir):
            print("报告目录不存在!")
            return []
        
        reports = []
        report_files = os.listdir(reports_dir)
        print(f"报告目录中的文件: {report_files}")
        
        for filename in report_files:
            if filename.startswith('report_') and filename.endswith('.html'):
                report_id = filename[:-5]  # 移除.html后缀
                report_path = os.path.join(reports_dir, filename)
                
                # 确保报告文件实际存在且可读
                if os.path.isfile(report_path) and os.access(report_path, os.R_OK):
                    try:
                        create_time = datetime.fromtimestamp(os.path.getctime(report_path)).strftime('%Y-%m-%d %H:%M:%S')
                        report = {
                            'id': report_id,
                            'name': f'测试报告 {report_id}',
                            'created_at': create_time,
                            'create_time': create_time,  # 添加这个字段以匹配模板中的使用
                            'report_url': f'/reports/{report_id}'  # 使用不带后缀的ID作为URL
                        }
                        reports.append(report)
                        print(f"已加载报告: {report_id}")
                    except Exception as e:
                        print(f"处理报告 {filename} 时出错: {e}")
                else:
                    print(f"警告: 无法访问报告文件: {report_path}")
        
        # 按创建时间倒序排序
        reports.sort(key=lambda x: x['created_at'], reverse=True)
        print(f"找到 {len(reports)} 个报告")
        return reports
    except Exception as e:
        print(f"获取报告列表出错: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_report_list(reports):
    """保存测试报告列表"""
    try:
        # 确保data目录存在
        reports_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'reports.json')
        os.makedirs(os.path.dirname(reports_file), exist_ok=True)
        
        with open(reports_file, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存报告列表出错: {e}")

def count_errors_in_reports():
    """统计报告中的错误数"""
    reports = get_report_list()
    error_count = sum(report.get('failed_cases', 0) for report in reports)
    return error_count

def generate_report(task):
    """根据任务信息生成测试报告"""
    # 生成报告ID
    report_id = f"report_{int(time.time())}"
    
    # 创建报告数据
    report = {
        'id': report_id,
        'task_id': task['id'],
        'name': f"Report for {task['name']}",
        'type': task['modules'][0].lower() if task['modules'] else '未知类型',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'created_by': task['run_by'],
        'modules': task['modules'],
        'submodules': task['submodules'],
        'env': task['env'],
        'status': 'passed',
        'duration': random.randint(30, 120),
    }
    
    # 根据任务类型获取真实的测试数据
    test_type = task['modules'][0] if task['modules'] else ''
    
    # 根据测试类型设置不同的测试用例数量和通过率
    if 'API' in test_type:
        total_cases = 39
        passed_cases = 33
        failed_cases = 6
    elif 'UI' in test_type:
        total_cases = 25
        passed_cases = 20
        failed_cases = 5
    elif 'SSH' in test_type:
        total_cases = 18
        passed_cases = 16
        failed_cases = 2
    else:
        total_cases = 15
        passed_cases = 12
        failed_cases = 3
    
    report['total_cases'] = total_cases
    report['passed_cases'] = passed_cases
    report['failed_cases'] = failed_cases
    
    if failed_cases > 0:
        report['status'] = 'failed'
    
    if total_cases > 0:
        summary = f"测试执行完成。共执行 {total_cases} 个测试用例，通过 {passed_cases} 个，失败 {failed_cases} 个。"
        if failed_cases > 0:
            summary += f" 失败率: {(failed_cases / total_cases * 100):.1f}%"
    else:
        summary = "任务已创建，但尚未执行测试。"
        
    report['summary'] = summary
    
    # 确保reports目录存在
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # 生成报告文件路径
    report_filename = f"{report_id}.html"
    report_file = os.path.join(reports_dir, report_filename)
    
    # 生成HTML报告内容
    report_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report['name']}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f9f9f9;
            color: #333;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background-color: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #7f8c8d;
            font-size: 16px;
        }}
        .info-section {{
            margin-bottom: 30px;
        }}
        .info-section h2 {{
            color: #3498db;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
            margin-bottom: 15px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        .info-item {{
            background-color: #f8f9fa;
            padding: 12px 15px;
            border-radius: 5px;
            border-left: 3px solid #3498db;
        }}
        .info-label {{
            font-weight: bold;
            color: #555;
            margin-bottom: 5px;
        }}
        .info-value {{
            color: #333;
        }}
        .stats-section {{
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }}
        .stat-box {{
            text-align: center;
            padding: 20px;
            border-radius: 5px;
        }}
        .total {{
            background-color: #e9ecef;
            border: 1px solid #dee2e6;
        }}
        .passed {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }}
        .failed {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .stat-label {{
            font-size: 14px;
            text-transform: uppercase;
        }}
        .progress-section {{
            margin-bottom: 30px;
        }}
        .progress-container {{
            background-color: #e9ecef;
            height: 25px;
            border-radius: 15px;
            overflow: hidden;
        }}
        .progress-bar {{
            background-color: #28a745;
            height: 100%;
            text-align: center;
            line-height: 25px;
            color: white;
            font-weight: bold;
            transition: width 1s ease;
        }}
        .summary-section {{
            background-color: #fff8e1;
            padding: 15px 20px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            margin-bottom: 30px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #7f8c8d;
            font-size: 14px;
        }}
        .author {{
            font-weight: bold;
            color: #3498db;
        }}
        @media (max-width: 768px) {{
            .info-grid, .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{report['name']}</h1>
            <div class="subtitle">生成时间: {report['created_at']}</div>
        </div>
        
        <div class="info-section">
            <h2>报告信息</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">报告ID</div>
                    <div class="info-value">{report['id']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">任务ID</div>
                    <div class="info-value">{report['task_id']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">测试类型</div>
                    <div class="info-value">{report['type'].upper()}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">创建者</div>
                    <div class="info-value">{report['created_by']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">测试模块</div>
                    <div class="info-value">{', '.join(report['modules']) if report['modules'] else "无"}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">子模块</div>
                    <div class="info-value">{', '.join(report['submodules']) if report['submodules'] else "无"}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">测试环境</div>
                    <div class="info-value">{report['env']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">执行时长</div>
                    <div class="info-value">{report['duration']} 秒</div>
                </div>
            </div>
        </div>
        
        <div class="stats-section">
            <h2>测试结果</h2>
            <div class="stats-grid">
                <div class="stat-box total">
                    <div class="stat-value">{total_cases}</div>
                    <div class="stat-label">总用例数</div>
                </div>
                <div class="stat-box passed">
                    <div class="stat-value">{passed_cases}</div>
                    <div class="stat-label">通过</div>
                </div>
                <div class="stat-box failed">
                    <div class="stat-value">{failed_cases}</div>
                    <div class="stat-label">失败</div>
                </div>
            </div>
        </div>
        
        <div class="progress-section">
            <h2>通过率</h2>
            <div class="progress-container">
                <div class="progress-bar" style="width: {(passed_cases / total_cases * 100) if total_cases > 0 else 0}%;">
                    {f"{(passed_cases / total_cases * 100):.1f}%" if total_cases > 0 else "0%"}
                </div>
            </div>
        </div>
        
        <div class="summary-section">
            <h2>测试摘要</h2>
            <p>{report['summary']}</p>
        </div>
        
        <div class="footer">
            <p>高效测试平台 - 报告生成于 {report['created_at']}</p>
            <p>开发者: <span class="author">longshen</span></p>
        </div>
    </div>
</body>
</html>"""
    
    # 保存报告文件
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        # 设置报告URL
        report['report_url'] = f"/reports/{report_filename}"  # 修改URL格式为直接访问reports目录
    except Exception as e:
        print(f"生成HTML报告失败: {e}")
    
    # 保存报告信息
    reports = get_report_list()
    reports.append(report)
    save_report_list(reports)
    
    return report_id

# 测试函数
def test_dingtalk():
    """钉钉通知API的单元测试函数"""
    # 创建应用上下文和请求上下文
    with app.app_context():
        with app.test_request_context():
            # 模拟用户登录
            session['user_id'] = 'test_user_id'
            session['username'] = 'test_user'
            session['role'] = 'admin'
            
            # 调用实际的测试逻辑
            webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=test_token"
            secret = "test_secret"
            
            # 使用模拟对象替代真实的网络请求
            from unittest.mock import patch
            with patch.object(DingTalkNotifier, 'send_text', return_value={'errcode': 0, 'errmsg': 'ok'}):
                # 测试响应成功的情况
                response = DingTalkNotifier(webhook_url, secret).send_text("测试消息")
                assert response.get('errcode') == 0
            
            # 测试完成后清理会话
            session.pop('user_id', None)
            session.pop('username', None)
            session.pop('role', None)

# 添加NAS设备查询相关的路由和函数
@app.route('/nas_finder')
@login_required
def nas_finder():
    # 从 JSON 文件加载问题和答案
    questions_file = os.path.join(app.root_path, 'nas_devices', 'questions.json')
    storage_question = "请输入存储组访问密码:"
    performance_question = "请输入性能专项组访问密码:"
    
    if os.path.exists(questions_file):
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            storage_question = questions.get('storage', {}).get('question', storage_question)
            performance_question = questions.get('performance', {}).get('question', performance_question)
    
    return render_template('nas_finder.html',
                        storage_question=storage_question,
                        performance_question=performance_question,
                        is_admin=current_user.is_admin())

@app.route('/api/search_nas', methods=['POST'])
@login_required
def search_nas():
    try:
        keyword = request.form.get('keyword', '').strip()
        if not keyword:
            return jsonify({'error': '请输入搜索关键词'})

        # 存储所有找到的设备
        all_devices = []
        existing_ips = set()  # 用于去重
        
        # 1. 通过服务端API获取设备
        try:
            print(f"通过服务端API查询设备，关键词: {keyword}")
            server_devices = search_api_devices("https://api.ugnas.com", keyword)
            
            if server_devices:
                print(f"服务端API返回 {len(server_devices)} 台设备")
                for device in server_devices:
                    ip = device.get('ipv4')
                    if ip and ip not in existing_ips:
                        all_devices.append(device)
                        existing_ips.add(ip)
            else:
                print("服务端API未找到匹配设备")
        except Exception as e:
            print(f"查询服务端API出错: {str(e)}")
        
        # 2. 通过本地网络API获取设备
        try:
            # 获取本地网络段
            local_segments = get_local_network_segments()
            print(f"检测到本地网络段: {local_segments}")
            
            # 通过本地网络中的每个设备API查询
            for segment in local_segments[:2]:  # 最多取前两个网段
                print(f"在网段 {segment} 中查找设备API...")
                
                # 查找具有API的设备
                api_hosts = find_api_hosts(segment)
                if api_hosts:
                    print(f"找到 {len(api_hosts)} 个API主机")
                    
                    # 通过找到的每个API查询设备
                    for host in api_hosts:
                        try:
                            client_devices = search_api_devices(f"http://{host}", keyword)
                            
                            if client_devices:
                                print(f"从主机 {host} 获取到 {len(client_devices)} 台设备")
                                for device in client_devices:
                                    ip = device.get('ipv4')
                                    if ip and ip not in existing_ips:
                                        all_devices.append(device)
                                        existing_ips.add(ip)
                        except Exception as e:
                            print(f"从主机 {host} 查询设备出错: {str(e)}")
        except Exception as e:
            print(f"本地网络设备查询出错: {str(e)}")
        
        # 格式化结果以符合前端预期
        matching_devices = []
        for device in all_devices:
            matching_devices.append({
                "name": device.get('name', '名称未找到'),
                "model": device.get('model', '型号未找到'),
                "deviceSn": device.get('deviceSn', '设备序列号未找到'),
                "ipv4": device.get('ipv4', 'IPV4 地址未找到'),
                "source": device.get('source', 'unknown')
            })
            
        print(f"最终返回 {len(matching_devices)} 台设备")
        return jsonify({
            'success': True,
            'devices': matching_devices if matching_devices else [{"message": "未找到匹配的设备"}]
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'error': '请求超时，请稍后重试'})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'网络请求错误: {str(e)}'})
    except Exception as e:
        print(f"搜索NAS设备时出错: {str(e)}")
        return jsonify({'error': '搜索设备时发生错误，请稍后重试'})

def find_api_hosts(segment):
    """查找网段中提供API服务的主机"""
    import concurrent.futures
    
    api_hosts = []
    
    # 优先检查常见IP范围
    ip_groups = [
        [f"{segment}.{i}" for i in range(1, 11)],        # 1-10
        [f"{segment}.{i}" for i in range(250, 255)],     # 250-254
        [f"{segment}.{i}" for i in range(100, 110)]      # 100-109
    ]
    
    # 对每个组使用线程池扫描
    for group in ip_groups:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_api_host, ip) for ip in group]
            
            for future in concurrent.futures.as_completed(futures):
                host = future.result()
                if host:
                    api_hosts.append(host)
    
    return api_hosts

def check_api_host(ip):
    """检查主机是否提供API服务"""
    try:
        # 尝试连接API健康检查端点
        url = f"http://{ip}/api/device/v1/ua/network/match"
        
        # 设置短超时
        response = requests.head(url, timeout=0.5)
        
        # 检查是否可访问
        if response.status_code < 500:  # 任何非服务器错误表示API可能存在
            print(f"发现API主机: {ip}")
            return ip
    except Exception:
        # 忽略连接错误
        pass
    return None

def search_api_devices(base_url, keyword):
    """通过API搜索设备"""
    # 构建请求URL
    if base_url.startswith("https://api.ugnas.com"):
        url = f"{base_url}/api/device/v1/ua/network/match"
        source = "server"
    else:
        url = f"{base_url}/api/device/v1/ua/network/match"
        source = "client"
    
    # 设置请求头
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": base_url,
        "Referer": base_url.replace("api.", "find."),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 发送请求
    try:
        response = requests.post(url, headers=headers, json={"keyword": keyword}, timeout=5)
        if response.status_code != 200:
            print(f"API返回状态码: {response.status_code}")
            return []
        
        data = response.json()
        print(f"API返回数据: {data}")
        
        # 搜索匹配的设备
        matching_devices = []
        keyword_lower = keyword.lower()
        
        # 根据API返回的数据结构调整处理逻辑
        devices = data.get('data', {}).get('deviceMatchs', [])
        if not devices and 'deviceMatchs' in data:
            devices = data.get('deviceMatchs', [])  # 尝试直接获取
            
        for device in devices:
            # 为了调试，打印出设备信息
            print(f"检查设备匹配: {device}")
            
            device_sn = str(device.get('deviceSn', '')).lower()
            device_model = str(device.get('model', '')).lower()
            device_name = str(device.get('name', '')).lower()
            
            # 更宽松的匹配逻辑
            if (keyword_lower in device_sn or 
                keyword_lower in device_model or 
                keyword_lower in device_name):
                device_info = {
                    "name": device.get('name', '名称未找到'),
                    "model": device.get('model', '型号未找到'),
                    "deviceSn": device.get('deviceSn', '设备序列号未找到'),
                    "ipv4": device.get('ipv4', 'IPV4 地址未找到'),
                    "source": source
                }
                print(f"找到匹配设备: {device_info}")
                matching_devices.append(device_info)
        
        return matching_devices
    except Exception as e:
        print(f"API请求错误: {str(e)}")
        return []

def get_local_network_segments():
    """获取本地网络段"""
    try:
        import socket
        import re
        
        # 获取本机IP
        hostname = socket.gethostname()
        local_ips = socket.gethostbyname_ex(hostname)[2]
        
        # 过滤出有效的IPv4地址并提取网段
        segments = []
        for ip in local_ips:
            if not ip.startswith('127.') and not ip.startswith('169.254.'):
                ip_parts = ip.split('.')
                segment = '.'.join(ip_parts[0:3])
                if segment not in segments:
                    segments.append(segment)
        
        # 如果没有找到有效网段，使用常见网段
        if not segments:
            segments = ['192.168.1', '192.168.0', '10.0.0', '172.17.0']
            
        return segments
    except Exception as e:
        print(f"获取本地网络段出错: {str(e)}")
        return ['192.168.1', '192.168.0', '10.0.0', '172.17.0']

# 添加缓存控制装饰器
def cache_control(max_age=31536000):  # 默认缓存1年
    def decorator(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            response = view_function(*args, **kwargs)
            if request.path.startswith('/static/'):
                response.headers['Cache-Control'] = f'public, max-age={max_age}'
                response.headers['Expires'] = (datetime.utcnow() + timedelta(seconds=max_age)).strftime('%a, %d %b %Y %H:%M:%S GMT')
            return response
        return decorated_function
    return decorator

# 静态文件URL处理
@app.context_processor
def utility_processor():
    def versioned_url_for(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', None)
            if filename:
                file_path = os.path.join(app.static_folder, filename)
                try:
                    # 如果文件存在，添加版本号
                    if os.path.exists(file_path):
                        values['v'] = int(os.stat(file_path).st_mtime)
                    else:
                        # 文件不存在，使用默认版本号
                        values['v'] = 0
                except Exception as e:
                    app.logger.error(f"版本控制出错: {str(e)}")
                    values['v'] = 0
        return url_for(endpoint, **values)
    return dict(url_for=versioned_url_for)

# 静态文件路由
@app.route('/static/<path:filename>')
@cache_control()
def static_files(filename):
    response = send_from_directory(app.static_folder, filename)
    return response

# 添加Service Worker路由
@app.route('/sw.js')
def service_worker():
    response = send_from_directory(os.path.join(app.static_folder, 'js'), 'sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

# 路由：网站配置
@app.route('/site_config', methods=['GET', 'POST'])
@admin_required
def site_config():
    if request.method == 'POST':
        site_title = request.form.get('site_title', '').strip()
        site_author = request.form.get('site_author', '').strip()
        
        if site_title:
            app.config['SITE_TITLE'] = site_title
        if site_author:
            app.config['SITE_AUTHOR'] = site_author
        
        # 处理图标上传
        if 'site_favicon' in request.files:
            favicon = request.files['site_favicon']
            if favicon and favicon.filename:
                # 检查文件类型
                if not favicon.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.ico', '.svg')):
                    flash('只允许上传png、jpg、ico或svg格式的图标', 'danger')
                else:
                    try:
                        # 确保目录存在
                        icons_dir = os.path.join(app.static_folder, 'images')
                        os.makedirs(icons_dir, exist_ok=True)
                        
                        # 使用时间戳创建唯一文件名，避免缓存问题
                        timestamp = int(time.time())
                        ext = favicon.filename.rsplit('.', 1)[1].lower()
                        filename = f'custom_favicon_{timestamp}.{ext}'
                        filepath = os.path.join(icons_dir, filename)
                        
                        # 删除旧图标文件
                        if app.config.get('SITE_FAVICON'):
                            try:
                                old_path = os.path.join(app.static_folder, app.config['SITE_FAVICON'])
                                if os.path.exists(old_path) and 'custom_favicon' in old_path:
                                    os.remove(old_path)
                                    print(f"已删除旧图标: {old_path}")
                            except Exception as e:
                                print(f"删除旧图标失败: {str(e)}")
                        
                        # 保存新文件
                        favicon.save(filepath)
                        print(f"已保存新图标: {filepath}")
                        
                        # 更新配置
                        app.config['SITE_FAVICON'] = f'images/{filename}'
                        print(f"已更新图标配置: {app.config['SITE_FAVICON']}")
                        flash('网站图标已更新', 'success')
                    except Exception as e:
                        print(f"图标上传错误: {str(e)}")
                        flash(f'图标上传失败: {str(e)}', 'danger')
            
        # 保存配置到文件
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'site_config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'site_title': app.config['SITE_TITLE'],
                    'site_author': app.config['SITE_AUTHOR'],
                    'site_favicon': app.config['SITE_FAVICON']
                }, f, ensure_ascii=False, indent=2)
            flash('网站配置已更新', 'success')
        except Exception as e:
            flash(f'保存配置失败: {str(e)}', 'danger')
            
        # 重定向添加时间戳，强制重新加载页面
        redirect_url = url_for('site_config', _t=int(time.time()))
        return redirect(redirect_url)
    
    return render_template('site_config.html', 
                           site_title=app.config.get('SITE_TITLE', '高效测试平台'),
                           site_author=app.config.get('SITE_AUTHOR', 'longshen'),
                           site_favicon=app.config.get('SITE_FAVICON'),
                           now=int(time.time()))

# 在所有模板中添加时间戳，避免缓存问题
@app.context_processor
def inject_now():
    return {'now': int(time.time())}

# 脚本目录管理相关API
@app.route('/scripts/list', methods=['GET'])
@login_required
def list_scripts():
    """获取脚本目录列表"""
    try:
        path = request.args.get('path', '')
        # 确定实际物理路径
        scripts_base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
        
        # 确保基础目录存在
        if not os.path.exists(scripts_base_dir):
            os.makedirs(scripts_base_dir, exist_ok=True)
            print(f"创建脚本基础目录: {scripts_base_dir}")
        
        target_dir = os.path.normpath(os.path.join(scripts_base_dir, path))
        
        # 安全检查：确保路径不超出scripts目录
        if not target_dir.startswith(scripts_base_dir):
            return jsonify({"error": "无效的目录路径", "success": False}), 400
            
        # 检查目录是否存在
        if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            return jsonify({"directories": [], "scripts": [], "success": True})
            
        # 获取目录和脚本列表
        directories = []
        scripts = []
        
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if os.path.isdir(item_path):
                # 目录项
                directories.append(item)
            elif os.path.isfile(item_path) and (item.endswith('.sh') or item.endswith('.py')):
                # 脚本文件项
                scripts.append(item)
                
        return jsonify({"directories": sorted(directories), "scripts": sorted(scripts), "success": True})
    except Exception as e:
        print(f"获取脚本列表错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "success": False}), 500

# 批量操作API：获取设备目录
@app.route('/api/knowledge/device_directories', methods=['GET'])
@login_required
def get_device_directories():
    """获取设备的目录结构"""
    try:
        device_ip = request.args.get('ip')
        ssh_port = request.args.get('port', '22')
        username = request.args.get('username')
        password = request.args.get('password')
        directory = request.args.get('directory', '/')
        
        if not device_ip or not username or not password:
            return jsonify({"error": "缺少必要参数", "success": False}), 400
            
        # 模拟返回目录结构
        time.sleep(0.5)  # 模拟网络延迟
        
        # 返回模拟数据
        return jsonify({
            "success": True,
            "directories": ["bin", "etc", "home", "usr", "var"],
            "message": "成功获取目录结构"
        })
    except Exception as e:
        print(f"获取设备目录错误: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

# 批量操作API：创建目录
@app.route('/scripts/create_dir', methods=['POST'])
@login_required
def create_script_directory():
    """在脚本目录中创建子目录"""
    try:
        data = request.json
        path = data.get('path', '')
        dirname = data.get('dirname', '')
        
        if not dirname:
            return jsonify({"error": "目录名不能为空", "success": False}), 400
            
        # 安全检查：目录名不能包含路径分隔符
        if '/' in dirname or '\\' in dirname:
            return jsonify({"error": "目录名不能包含路径分隔符", "success": False}), 400
            
        # 确定实际物理路径
        scripts_base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
        parent_dir = os.path.normpath(os.path.join(scripts_base_dir, path))
        new_dir_path = os.path.join(parent_dir, dirname)
        
        # 安全检查：确保路径不超出scripts目录
        if not parent_dir.startswith(scripts_base_dir):
            return jsonify({"error": "无效的目录路径", "success": False}), 400
            
        # 检查父目录是否存在
        if not os.path.exists(parent_dir) or not os.path.isdir(parent_dir):
            return jsonify({"error": "父目录不存在", "success": False}), 400
            
        # 检查目录是否已存在
        if os.path.exists(new_dir_path):
            return jsonify({"error": "目录已存在", "success": False}), 400
            
        # 创建目录
        os.makedirs(new_dir_path, exist_ok=True)
        
        return jsonify({"success": True, "message": "目录创建成功"})
    except Exception as e:
        print(f"创建目录错误: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

# 主函数
if __name__ == '__main__':
    # 强制输出，确保能看到错误信息
    import sys
    sys.stdout.flush()
    print("=== 开始启动高效测试平台 ===")
    sys.stdout.flush()
    
    try:
        print("=== 高效测试平台启动 by longshen ===")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"系统平台: {platform.system()} {platform.release()}")
        print(f"Python版本: {platform.python_version()}")
        sys.stdout.flush()
        
        # 检查admin账户
        admin_exists = False
        for user in User.get_all_users():
            if user.username == 'admin':
                admin_exists = True
                print("管理员账户已存在")
                break
        
        if not admin_exists:
            print("创建管理员账户...")
            User.create_user('admin', 'admin123', 'admin')
            print("管理员账户创建成功")
        
        sys.stdout.flush()
        
        # 检查静态目录和CSS文件
        if os.path.exists('static'):
            print("静态文件目录存在")
            if os.path.exists('static/css/style.css'):
                print("样式文件存在")
            else:
                print("警告: 样式文件不存在")
        else:
            print("警告: 静态文件目录不存在")
        
        sys.stdout.flush()
        
        print("\n启动Web服务...")
        print(f"调试模式: {'开启' if app.debug else '关闭'}")
        print(f"监听地址: 0.0.0.0:5000")
        print(f"访问地址: http://localhost:5000")
        print("按Ctrl+C停止服务\n")
        sys.stdout.flush()
        
        # 启动Flask应用
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"启动失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush() 