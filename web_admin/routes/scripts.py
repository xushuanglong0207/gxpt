import os
import shutil
import subprocess
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from functools import wraps
import paramiko
import threading
import uuid
import traceback
import re
import time

scripts_bp = Blueprint('scripts', __name__)

# 脚本存储根目录 - 直接指向static目录，不包含scripts
SCRIPTS_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
# 确保scripts根目录存在
scripts_dir = os.path.join(SCRIPTS_ROOT, 'scripts')
os.makedirs(scripts_dir, exist_ok=True)

# 用于避免路径混淆的工具函数
def clean_path(path):
    """清理并规范化路径，去除重复的scripts部分和特殊字符"""
    # 替换反斜杠和规范化
    path = path.replace('\\', '/').strip()
    # 移除连续的scripts
    path = path.replace('scriptsscripts', 'scripts')
    # 处理/scripts/scripts格式
    if path.startswith('/scripts/scripts'):
        path = '/scripts' + path[16:] # 去掉第二个scripts
    # 确保以/scripts开头
    if not path.startswith('/scripts'):
        path = '/scripts' + ('' if path.startswith('/') else '/') + path
    # 处理连续斜杠
    path = path.replace('//', '/')
    # 移除空白和控制字符
    path = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', path)
    return path

# 将Web路径转换为文件系统路径
def web_to_fs_path(web_path):
    """将Web路径(/scripts/...)转换为文件系统路径"""
    web_path = clean_path(web_path)
    if web_path.startswith('/scripts/'):
        rel_path = web_path[9:] # 去掉/scripts/
        return os.path.join(SCRIPTS_ROOT, 'scripts', rel_path)
    return os.path.join(SCRIPTS_ROOT, 'scripts') # 默认返回scripts根目录

# 导入登录检查装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 简单实现，实际应该检查用户是否登录
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 简单实现，实际应该检查用户是否是管理员
        return f(*args, **kwargs)
    return decorated_function

# 获取脚本列表 - 同时支持多个路径
@scripts_bp.route('/scripts/list', methods=['GET'])
@scripts_bp.route('/api/scripts/list', methods=['GET'])
@scripts_bp.route('/api/knowledge/scripts', methods=['GET'])
@login_required
def get_scripts():
    # 支持path参数和directory参数
    path = request.args.get('path', '')
    directory = request.args.get('directory', '')
    
    # 合并参数 - 优先使用directory
    if directory:
        web_path = directory
    elif path:
        web_path = '/scripts/' + path.lstrip('/')
    else:
        web_path = '/scripts'
    
    # 使用统一的路径清理函数处理Web路径
    clean_web_path = clean_path(web_path)
    print(f"清理后的Web路径: {clean_web_path}")
    
    # 转换为文件系统路径
    fs_path = web_to_fs_path(clean_web_path)
    print(f"转换为文件系统路径: {fs_path}")
    
    # 检查目录是否存在
    if not os.path.exists(fs_path):
        print(f"创建目录: {fs_path}")
        os.makedirs(fs_path, exist_ok=True)
    
    if not os.path.isdir(fs_path):
        return jsonify({'error': '指定的路径不是一个目录'}), 400
    
    try:
        directories = []
        scripts = []
        
        # 获取目录和脚本文件
        for item in os.listdir(fs_path):
            item_path = os.path.join(fs_path, item)
            if os.path.isdir(item_path):
                directories.append(item)
            else:
                # 只收集脚本文件
                if item.endswith(('.sh', '.py', '.bat', '.cmd', '.ps1')):
                    scripts.append(item)
        
        print(f"在 {fs_path} 中找到 {len(directories)} 个目录和 {len(scripts)} 个脚本")
        
        return jsonify({
            'directories': sorted(directories),
            'scripts': sorted(scripts)
        })
    except Exception as e:
        current_app.logger.error(f"获取脚本列表出错: {str(e)}")
        print(f"获取脚本列表错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 创建脚本目录 - 同时支持多个路径
@scripts_bp.route('/scripts/directory', methods=['POST'])
@scripts_bp.route('/api/scripts/directory', methods=['POST'])
@scripts_bp.route('/api/scripts/create_directory', methods=['POST'])
@scripts_bp.route('/api/knowledge/scripts/directory', methods=['POST'])
@login_required
def create_directory():
    # 支持form和json两种方式
    if request.is_json:
        data = request.json
        parent_path = data.get('parentPath', '')
        dir_name = data.get('dirName', '')
        # 兼容path参数
        path = data.get('path', '')
        if path and not parent_path and not dir_name:
            if '/' in path:
                parent_path, dir_name = path.rsplit('/', 1)
            else:
                parent_path = '/scripts'
                dir_name = path
    else:
        parent_path = request.form.get('directory_path', '')
        parent_path2 = request.form.get('parent_path', '')
        dir_name = request.form.get('dir_name', '')
        
        if parent_path2 and dir_name:
            parent_path = parent_path2
        elif parent_path and '/' in parent_path:
            parent_path, dir_name = parent_path.rsplit('/', 1)
    
    print(f"创建目录，父目录: {parent_path}, 目录名: {dir_name}")
    
    if not dir_name:
        return jsonify({'success': False, 'message': '目录名称不能为空'}), 400
    
    # 验证目录名称
    if not all(c.isalnum() or c == '_' or c == '-' for c in dir_name):
        return jsonify({'success': False, 'message': '目录名称只能包含字母、数字、下划线和连字符'}), 400
    
    # 使用统一的路径清理函数处理父目录路径
    parent_web_path = clean_path(parent_path or '/scripts')
    print(f"清理后的父目录Web路径: {parent_web_path}")
    
    # 构建新目录的Web路径
    new_dir_web_path = f"{parent_web_path}/{dir_name}"
    print(f"新目录的Web路径: {new_dir_web_path}")
    
    # 转换为文件系统路径
    parent_fs_path = web_to_fs_path(parent_web_path)
    new_dir_fs_path = os.path.join(parent_fs_path, dir_name)
    print(f"父目录文件系统路径: {parent_fs_path}")
    print(f"新目录文件系统路径: {new_dir_fs_path}")
    
    # 检查父目录是否存在
    if not os.path.exists(parent_fs_path):
        os.makedirs(parent_fs_path, exist_ok=True)
    
    # 检查新目录是否已存在
    if os.path.exists(new_dir_fs_path):
        return jsonify({'success': False, 'message': '目录已存在'}), 409
    
    try:
        os.makedirs(new_dir_fs_path, exist_ok=True)
        print(f"目录创建成功: {new_dir_fs_path}")
        return jsonify({'success': True, 'message': '目录创建成功'})
    except Exception as e:
        print(f"创建目录出错: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

# 上传脚本文件 - 同时支持多个路径
@scripts_bp.route('/scripts/upload', methods=['POST'])
@scripts_bp.route('/api/scripts/upload', methods=['POST'])
@scripts_bp.route('/api/knowledge/scripts/upload', methods=['POST'])
@login_required
def upload_script():
    upload_path = request.form.get('uploadPath', '')
    upload_dir = request.form.get('uploadDirectory', '')
    
    # 合并参数
    if upload_dir:
        upload_path = upload_dir
    
    if not upload_path:
        upload_path = '/scripts'
    
    if 'scriptFile' not in request.files:
        return jsonify({'success': False, 'message': '没有找到上传的文件'}), 400
    
    script_file = request.files['scriptFile']
    
    if script_file.filename == '':
        return jsonify({'success': False, 'message': '未选择文件'}), 400
    
    filename = secure_filename(script_file.filename)
    
    # 检查文件扩展名
    allowed_extensions = ['.sh', '.py', '.bat', '.cmd', '.ps1']
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return jsonify({'success': False, 'message': f'文件类型不允许，只支持以下类型: {", ".join(allowed_extensions)}'}), 400
    
    # 规范化路径
    if upload_path.startswith('/scripts'):
        upload_path = upload_path[1:]  # 去掉开头的斜杠
    elif upload_path == '':
        upload_path = 'scripts'
    
    absolute_upload_path = os.path.join(SCRIPTS_ROOT, upload_path)
    
    # 检查目录是否存在
    if not os.path.exists(absolute_upload_path):
        os.makedirs(absolute_upload_path, exist_ok=True)
    
    file_path = os.path.join(absolute_upload_path, filename)
    
    try:
        script_file.save(file_path)
        
        # 为脚本文件添加执行权限(Linux/Unix)
        if os.name != 'nt':
            os.chmod(file_path, 0o755)
        
        return jsonify({'success': True, 'message': '文件上传成功'})
    except Exception as e:
        current_app.logger.error(f"上传脚本出错: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# 删除脚本或目录 - 同时支持多个路径
@scripts_bp.route('/scripts/delete', methods=['POST', 'DELETE'])
@scripts_bp.route('/api/scripts/delete', methods=['POST', 'DELETE'])
@scripts_bp.route('/api/knowledge/scripts', methods=['DELETE'])
@login_required
def delete_script():
    # 打印脚本根目录
    print(f"SCRIPTS_ROOT: {SCRIPTS_ROOT}")
    
    # 根据请求方法获取数据
    if request.method == 'DELETE':
        data = request.json if request.is_json else {}
    else:  # POST
        data = request.json if request.is_json else {}
    
    # 如果请求体为空，尝试从URL参数获取
    path = data.get('path', request.args.get('path', ''))
    is_directory = data.get('isDirectory', request.args.get('isDirectory', 'false').lower() == 'true')
    
    print(f"原始请求路径: {path}, 是目录: {is_directory}")
    
    if not path:
        return jsonify({'success': False, 'message': '路径不能为空'}), 400
    
    # 尝试多种路径组合
    possible_paths = []
    
    # 原始处理逻辑
    processed_path = path
    if processed_path.startswith('/scripts/'):
        processed_path = processed_path[9:]  # 去掉/scripts/
    elif processed_path.startswith('/scripts'):
        processed_path = processed_path[8:]  # 去掉/scripts
    elif processed_path.startswith('scripts/'):
        processed_path = processed_path[8:]
    elif processed_path.startswith('scripts'):
        processed_path = processed_path[7:]
    
    # 去掉可能的开头斜杠
    if processed_path.startswith('/'):
        processed_path = processed_path[1:]
    
    # 添加可能的路径
    possible_paths.append(os.path.join(SCRIPTS_ROOT, processed_path))
    possible_paths.append(os.path.join(SCRIPTS_ROOT, 'scripts', processed_path))
    
    # 去掉scripts前缀的处理
    if path.startswith('/scripts/'):
        possible_paths.append(os.path.join(SCRIPTS_ROOT, path[9:]))
    
    # 直接使用原始路径
    possible_paths.append(os.path.join(SCRIPTS_ROOT, path))
    
    # 检查哪些路径存在
    absolute_path = None
    for test_path in possible_paths:
        print(f"测试路径: {test_path}")
        if os.path.exists(test_path):
            absolute_path = test_path
            print(f"找到存在的路径: {absolute_path}")
            break
    
    if not absolute_path:
        print(f"所有可能的路径都不存在")
        return jsonify({'success': False, 'message': '路径不存在'}), 404
    
    try:
        if os.path.isdir(absolute_path):
            print(f"删除目录: {absolute_path}")
            shutil.rmtree(absolute_path)
        else:
            print(f"删除文件: {absolute_path}")
            os.remove(absolute_path)
        
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        print(f"删除出错: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# 部署目录到设备 - 支持多个路径
@scripts_bp.route('/scripts/deploy', methods=['POST'])
@scripts_bp.route('/api/scripts/deploy', methods=['POST'])
@login_required
def deploy_directory():
    data = request.json
    source_directory = data.get('sourceDirectory', '')
    target_path = data.get('targetPath', '/test')
    devices = data.get('devices', [])
    
    print(f"收到部署请求:")
    print(f"源目录: {source_directory}")
    print(f"目标路径: {target_path}")
    print(f"设备数量: {len(devices)}")
    print(f"设备列表: {devices}")
    
    if not source_directory:
        return jsonify({'success': False, 'message': '源目录不能为空'}), 400
    
    if not devices:
        return jsonify({'success': False, 'message': '请选择要部署的设备'}), 400
    
    print(f"SCRIPTS_ROOT: {SCRIPTS_ROOT}")
    
    # 规范化路径
    if source_directory.startswith('/scripts/'):
        source_directory = source_directory[9:]  # 去掉/scripts/前缀
    elif source_directory.startswith('/scripts'):
        source_directory = source_directory[8:]  # 去掉/scripts前缀
    elif source_directory.startswith('scripts/'):
        source_directory = source_directory[8:]  # 去掉scripts/前缀
    
    print(f"规范化后的源目录: {source_directory}")
    
    # 拼接完整路径 - 使用正确的路径分隔符
    absolute_source_dir = os.path.normpath(os.path.join(SCRIPTS_ROOT, 'scripts', source_directory))
    print(f"绝对源目录路径: {absolute_source_dir}")
    
    # 获取源目录名称（取最后一个目录名）
    source_dir_name = os.path.basename(source_directory) if source_directory else ""
    print(f"源目录名称: {source_dir_name}")
    
    # 如果有源目录名，将其添加到目标路径
    destination_path = target_path
    if source_dir_name:
        destination_path = os.path.join(target_path, source_dir_name).replace('\\', '/')
        print(f"完整目标路径（包含源目录名）: {destination_path}")
    
    # 检查源目录是否存在，如果不存在则创建
    if not os.path.exists(absolute_source_dir):
        try:
            os.makedirs(absolute_source_dir, exist_ok=True)
            print(f"源目录不存在，已自动创建: {absolute_source_dir}")
        except Exception as e:
            print(f"创建源目录失败: {str(e)}")
            return jsonify({'success': False, 'message': f'创建源目录失败: {str(e)}'}), 500
    
    # 检查是否是目录
    if not os.path.isdir(absolute_source_dir):
        return jsonify({'success': False, 'message': '指定的源路径不是一个目录'}), 400
    
    # 检查目录中是否有文件
    has_files = False
    for root, _, files in os.walk(absolute_source_dir):
        if files:
            has_files = True
            break
    
    if not has_files:
        print(f"警告: 源目录 '{absolute_source_dir}' 中没有任何文件可以部署")
        # 返回提示信息而不是错误，因为这可能是预期行为
        return jsonify({
            'success': True,
            'warning': '源目录中没有任何文件可以部署',
            'results': []
        })
    
    # 递归打印目录结构，用于调试
    print(f"源目录 '{absolute_source_dir}' 中的文件结构:")
    for root, dirs, files in os.walk(absolute_source_dir):
        print(f"目录: {root}")
        print(f"  子目录: {dirs}")
        print(f"  文件: {files}")
    
    # 线程函数：部署目录到单个设备
    def deploy_to_device(device, results):
        try:
            ip = device.get('ip')
            username = device.get('username')
            password = device.get('password')
            ssh_port = int(device.get('sshPort', 22))
            
            # 创建SSH客户端
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接到设备
            try:
                print(f"正在连接设备: {ip}:{ssh_port}")
                ssh.connect(ip, port=ssh_port, username=username, password=password, timeout=10)
                print(f"成功连接到设备: {ip}")
            except Exception as conn_e:
                error_msg = f'连接失败: {str(conn_e)}'
                print(error_msg)
                traceback.print_exc()
                results.append({
                    'ip': ip,
                    'status': '执行失败',
                    'message': error_msg
                })
                return
            
            # 创建SFTP客户端
            sftp = ssh.open_sftp()
            
            try:
                # 使用更直接的方式处理文件上传，不依赖os.walk
                # 获取源目录下的所有文件和目录
                for root, dirs, files in os.walk(absolute_source_dir):
                    print(f"处理目录: {root}, 包含 {len(files)} 个文件")
                    # 如果files为空，记录并继续
                    if not files:
                        print(f"警告: 目录 {root} 中没有文件")
                        continue
                        
                    # 计算相对路径
                    rel_path = os.path.relpath(root, absolute_source_dir)
                    remote_dir = destination_path
                    if rel_path != '.':
                        remote_dir = os.path.join(destination_path, rel_path).replace('\\', '/')
                    
                    # 始终创建远程目录，无论是否为根目录
                    print(f"创建远程目录: {remote_dir}")
                    mkdir_cmd = f'echo "{password}" | sudo -S mkdir -p "{remote_dir}" && echo "{password}" | sudo -S chmod 755 "{remote_dir}"'
                    stdin, stdout, stderr = ssh.exec_command(mkdir_cmd, get_pty=True)
                    exit_status = stdout.channel.recv_exit_status()
                    if exit_status != 0:
                        stderr_output = stderr.read().decode()
                        print(f"创建目录失败: {stderr_output}")
                        # 尝试另一种方式创建目录
                        print("尝试使用sudo -i方式创建目录...")
                        alt_mkdir_cmd = f'echo "{password}" | sudo -S -i sh -c "mkdir -p {remote_dir} && chmod 755 {remote_dir}"'
                        stdin, stdout, stderr = ssh.exec_command(alt_mkdir_cmd, get_pty=True)
                        exit_status = stdout.channel.recv_exit_status()
                        if exit_status != 0:
                            stderr_output = stderr.read().decode()
                            print(f"创建目录再次失败: {stderr_output}")
                    
                    # 验证目录是否存在
                    check_dir_cmd = f'echo "{password}" | sudo -S -i sh -c "ls -la {remote_dir}"'
                    stdin, stdout, stderr = ssh.exec_command(check_dir_cmd, get_pty=True)
                    print(f"远程目录内容: {stdout.read().decode()}")
                    print(f"远程目录错误: {stderr.read().decode()}")
                    
                    # 上传当前目录下的文件
                    for filename in files:
                        try:
                            # 构建完整的本地文件路径
                            local_path = os.path.join(root, filename)
                            # 构建目标路径
                            remote_path = os.path.join(remote_dir, filename).replace('\\', '/')
                            
                            # 验证本地文件存在
                            if not os.path.isfile(local_path):
                                print(f"警告: 本地文件不存在 {local_path}")
                                print(f"目录内容: {os.listdir(os.path.dirname(local_path))}")
                                continue
                                
                            # 输出调试信息
                            print(f"上传文件: {local_path} -> {remote_path}")
                            print(f"文件大小: {os.path.getsize(local_path)} 字节")
                            
                            # 设置文件权限值 - 在try块外部定义以便在异常处理中也能使用
                            chmod_val = '755' if filename.endswith(('.sh', '.py', '.pl', '.rb')) else '644'
                            
                            # 使用临时文件和cat命令的方式上传文件
                            try:
                                # 使用sftp上传
                                sftp.put(local_path, remote_path)
                                print(f"SFTP上传完成: {remote_path}")
                                
                                # 检查远程文件是否存在
                                check_cmd = f'echo "{password}" | sudo -S ls -l "{remote_path}"'
                                stdin, stdout, stderr = ssh.exec_command(check_cmd)
                                check_output = stdout.read().decode()
                                check_error = stderr.read().decode()
                                print(f"检查远程文件: {check_output}")
                                if check_error:
                                    print(f"检查远程文件错误: {check_error}")
                                
                                # 设置文件权限
                                chmod_cmd = f'echo "{password}" | sudo -S chmod {chmod_val} "{remote_path}"'
                                stdin, stdout, stderr = ssh.exec_command(chmod_cmd)
                                chmod_error = stderr.read().decode()
                                if chmod_error:
                                    print(f"设置文件权限错误: {chmod_error}")
                                print(f"文件权限设置完成: {remote_path}")
                            except Exception as upload_e:
                                print(f"SFTP上传失败，尝试使用SSH命令方式: {str(upload_e)}")
                                
                                # 如果SFTP失败，尝试使用SSH命令方式上传
                                with open(local_path, 'rb') as f:
                                    file_content = f.read()
                                    # 使用base64编码文件内容
                                    import base64
                                    encoded_content = base64.b64encode(file_content).decode()
                                    
                                    # 通过命令将base64内容解码并写入文件，使用绝对路径避免依赖home目录
                                    # 使用sudo sh -c来避免依赖.bashrc文件
                                    cat_cmd = f'echo "{password}" | sudo -S sh -c "/usr/bin/echo \'{encoded_content}\' | /usr/bin/base64 -d > {remote_path} && /bin/chmod {chmod_val} {remote_path}"'
                                    
                                    # 使用get_pty=True来避免某些终端相关问题
                                    stdin, stdout, stderr = ssh.exec_command(cat_cmd, get_pty=True)
                                    exit_status = stdout.channel.recv_exit_status()
                                    stderr_output = stderr.read().decode()
                                    
                                    if exit_status != 0:
                                        print(f"SSH命令上传失败，退出码: {exit_status}，错误: {stderr_output}")
                                        
                                        # 尝试直接切换到root用户上传
                                        print("尝试使用su方式切换到root用户上传...")
                                        su_cmd = f'echo "{password}" | su -c "/usr/bin/echo \'{encoded_content}\' | /usr/bin/base64 -d > {remote_path} && /bin/chmod {chmod_val} {remote_path}"'
                                        stdin, stdout, stderr = ssh.exec_command(su_cmd, get_pty=True)
                                        exit_status = stdout.channel.recv_exit_status()
                                        stderr_output = stderr.read().decode()
                                        
                                        if exit_status != 0:
                                            print(f"使用su命令上传失败: {stderr_output}")
                                            
                                            # 最后一次尝试，使用sudo -i
                                            print("尝试使用sudo -i绕过bashrc...")
                                            sudo_i_cmd = f'echo "{password}" | sudo -S -i bash -c "/usr/bin/echo \'{encoded_content}\' | /usr/bin/base64 -d > {remote_path} && /bin/chmod {chmod_val} {remote_path}"'
                                            stdin, stdout, stderr = ssh.exec_command(sudo_i_cmd, get_pty=True)
                                            exit_status = stdout.channel.recv_exit_status()
                                            stderr_output = stderr.read().decode()
                                            
                                            if exit_status != 0:
                                                print(f"使用sudo -i命令上传失败: {stderr_output}")
                                                raise Exception(f"SSH命令上传失败: {stderr_output}")
                                    
                                    print(f"SSH命令上传完成: {remote_path}")
                            
                        except FileNotFoundError as e:
                            print(f"文件不存在: {local_path}")
                            print(f"错误详情: {str(e)}")
                            # 继续处理其他文件
                        except Exception as e:
                            error_msg = f'上传文件 {filename} 失败: {str(e)}'
                            print(f"设备 {ip} 上传失败: {error_msg}")
                            results.append({
                                'ip': ip,
                                'success': False,
                                'message': error_msg
                            })
                            return
                
                success_msg = f'目录 {source_directory} 成功部署到 {destination_path}'
                print(f"设备 {ip} 部署成功: {success_msg}")
                results.append({
                    'ip': ip,
                    'success': True,
                    'message': success_msg
                })
            finally:
                sftp.close()
                ssh.close()
        except Exception as e:
            error_msg = f'部署过程出现异常: {str(e)}'
            print(f"设备 {ip} 部署异常: {error_msg}")
            results.append({
                'ip': ip,
                'success': False,
                'message': error_msg
            })
    
    # 启动多线程并行部署
    results = []
    threads = []
    
    for device in devices:
        thread = threading.Thread(target=deploy_to_device, args=(device, results))
        thread.start()
        threads.append(thread)
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    return jsonify({
        'success': True,
        'results': results
    })

# 部署脚本到设备
@scripts_bp.route('/api/knowledge/scripts/deploy', methods=['POST'])
@login_required
def deploy_script():
    data = request.json
    script_path = data.get('scriptPath')
    devices = data.get('devices', [])
    target_path = data.get('targetPath', '/test')  # 添加目标路径参数，默认为/test
    
    print(f"收到单文件部署请求:")
    print(f"脚本路径: {script_path}")
    print(f"目标路径: {target_path}")
    print(f"设备数量: {len(devices)}")
    
    if not script_path:
        return jsonify({'success': False, 'message': '脚本路径不能为空'}), 400
    
    if not devices:
        return jsonify({'success': False, 'message': '请选择要部署的设备'}), 400
    
    # 规范化路径
    if script_path.startswith('/scripts/'):
        script_path = script_path[9:]  # 去掉/scripts/前缀
    elif script_path.startswith('/scripts'):
        script_path = script_path[8:]  # 去掉/scripts前缀
    elif script_path.startswith('scripts/'):
        script_path = script_path[8:]  # 去掉scripts/前缀
    
    print(f"规范化后的脚本路径: {script_path}")
    
    # 拼接完整路径
    absolute_script_path = os.path.normpath(os.path.join(SCRIPTS_ROOT, 'scripts', script_path))
    print(f"绝对脚本路径: {absolute_script_path}")
    
    # 检查脚本是否存在
    if not os.path.exists(absolute_script_path):
        print(f"脚本文件不存在: {absolute_script_path}")
        # 打印目录内容以便调试
        try:
            parent_dir = os.path.dirname(absolute_script_path)
            if os.path.exists(parent_dir):
                print(f"父目录存在: {parent_dir}")
                print(f"目录内容: {os.listdir(parent_dir)}")
        except Exception as e:
            print(f"检查父目录时出错: {str(e)}")
        return jsonify({'success': False, 'message': f'脚本文件不存在: {absolute_script_path}'}), 404
    
    if not os.path.isfile(absolute_script_path):
        print(f"指定的路径不是文件: {absolute_script_path}")
        return jsonify({'success': False, 'message': '指定的路径不是一个脚本文件'}), 404
    
    # 获取脚本文件名
    script_filename = os.path.basename(script_path)
    print(f"脚本文件名: {script_filename}")
    
    # 线程函数：部署脚本到单个设备
    def deploy_to_device(device, results):
        try:
            ip = device.get('ip')
            username = device.get('username')
            password = device.get('password')
            ssh_port = int(device.get('sshPort', 22))
            
            # 创建SSH客户端
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接到设备
            try:
                print(f"正在连接设备: {ip}:{ssh_port}")
                ssh.connect(ip, port=ssh_port, username=username, password=password, timeout=10)
                print(f"成功连接到设备: {ip}")
            except Exception as conn_e:
                error_msg = f'连接失败: {str(conn_e)}'
                print(error_msg)
                traceback.print_exc()
                results.append({
                    'ip': ip,
                    'status': '执行失败',
                    'message': error_msg
                })
                return
            
            # 创建SFTP客户端
            sftp = ssh.open_sftp()
            
            try:
                # 确保目标目录存在，而不是默认/opt/scripts
                print(f"确保目标目录存在: {target_path}")
                mkdir_cmd = f'echo "{password}" | sudo -S mkdir -p "{target_path}" && echo "{password}" | sudo -S chmod 755 "{target_path}"'
                stdin, stdout, stderr = ssh.exec_command(mkdir_cmd, get_pty=True)
                exit_status = stdout.channel.recv_exit_status()
                stderr_str = stderr.read().decode()

                if exit_status != 0:
                    # 目录创建失败，尝试另一种方式
                    print(f"创建目录失败，尝试sudo -i方式...")
                    alt_mkdir_cmd = f'echo "{password}" | sudo -S -i bash -c "mkdir -p {target_path} && chmod 755 {target_path}"'
                    stdin, stdout, stderr = ssh.exec_command(alt_mkdir_cmd, get_pty=True)
                    exit_status = stdout.channel.recv_exit_status()
                    stderr_str = stderr.read().decode()
                    
                    if exit_status != 0:
                        detailed_error = stderr_str or f"命令执行失败，退出码: {exit_status}"
                        detailed_error = detailed_error.replace('[sudo] password for ' + username + ': ', '').strip()
                        error_msg = f'创建目录失败: {detailed_error}'
                        print(f"设备 {ip} 创建目录失败: {error_msg}")
                        results.append({
                            'ip': ip,
                            'success': False,
                            'message': error_msg
                        })
                        return
                
                # 检查目录是否成功创建
                check_dir_cmd = f'echo "{password}" | sudo -S ls -la "{target_path}"'
                stdin, stdout, stderr = ssh.exec_command(check_dir_cmd, get_pty=True)
                dir_output = stdout.read().decode()
                print(f"目标目录内容: {dir_output}")
                
                # 传输脚本文件到目标目录
                remote_path = f'{target_path}/{script_filename}'
                try:
                    print(f"开始上传文件: {absolute_script_path} -> {remote_path}")
                    print(f"文件大小: {os.path.getsize(absolute_script_path)} 字节")
                    sftp.put(absolute_script_path, remote_path)
                    print(f"SFTP上传完成: {remote_path}")
                except Exception as upload_e:
                    print(f"SFTP上传失败，尝试使用SSH命令方式: {str(upload_e)}")
                    
                    # 如果SFTP失败，尝试使用SSH命令方式上传
                    try:
                        with open(absolute_script_path, 'rb') as f:
                            file_content = f.read()
                            # 使用base64编码文件内容
                            import base64
                            encoded_content = base64.b64encode(file_content).decode()
                            
                            # 设置文件权限值
                            chmod_val = '755'  # 脚本文件默认权限
                            
                            # 通过命令将base64内容解码并写入文件，使用绝对路径避免依赖home目录
                            # 使用sudo sh -c来避免依赖.bashrc文件
                            cat_cmd = f'echo "{password}" | sudo -S sh -c "/usr/bin/echo \'{encoded_content}\' | /usr/bin/base64 -d > {remote_path} && /bin/chmod {chmod_val} {remote_path}"'
                            
                            # 使用get_pty=True来避免某些终端相关问题
                            stdin, stdout, stderr = ssh.exec_command(cat_cmd, get_pty=True)
                            exit_status = stdout.channel.recv_exit_status()
                            stderr_output = stderr.read().decode()
                            
                            if exit_status != 0:
                                print(f"SSH命令上传失败，退出码: {exit_status}，错误: {stderr_output}")
                                
                                # 尝试直接切换到root用户上传
                                print("尝试使用su方式切换到root用户上传...")
                                su_cmd = f'echo "{password}" | su -c "/usr/bin/echo \'{encoded_content}\' | /usr/bin/base64 -d > {remote_path} && /bin/chmod {chmod_val} {remote_path}"'
                                stdin, stdout, stderr = ssh.exec_command(su_cmd, get_pty=True)
                                exit_status = stdout.channel.recv_exit_status()
                                stderr_output = stderr.read().decode()
                                
                                if exit_status != 0:
                                    print(f"使用su命令上传失败: {stderr_output}")
                                    
                                    # 最后一次尝试，使用sudo -i
                                    print("尝试使用sudo -i绕过bashrc...")
                                    sudo_i_cmd = f'echo "{password}" | sudo -S -i bash -c "/usr/bin/echo \'{encoded_content}\' | /usr/bin/base64 -d > {remote_path} && /bin/chmod {chmod_val} {remote_path}"'
                                    stdin, stdout, stderr = ssh.exec_command(sudo_i_cmd, get_pty=True)
                                    exit_status = stdout.channel.recv_exit_status()
                                    stderr_output = stderr.read().decode()
                                    
                                    if exit_status != 0:
                                        print(f"使用sudo -i命令上传失败: {stderr_output}")
                                        raise Exception(f"SSH命令上传失败: {stderr_output}")
                            
                            print(f"SSH命令上传完成: {remote_path}")
                    except Exception as e:
                        error_msg = f'脚本上传失败: {str(e)}'
                        print(f"设备 {ip} 上传脚本失败: {error_msg}")
                        results.append({
                            'ip': ip,
                            'success': False,
                            'message': error_msg
                        })
                        return
                
                # 设置脚本执行权限
                chmod_cmd = f'echo "{password}" | sudo -S chmod 755 "{remote_path}"'
                print(f"设置文件权限: {chmod_cmd}")
                stdin, stdout, stderr = ssh.exec_command(chmod_cmd, get_pty=True)
                exit_status = stdout.channel.recv_exit_status()
                stderr_str = stderr.read().decode()

                if exit_status != 0:
                    detailed_error = stderr_str or f"命令执行失败，退出码: {exit_status}"
                    detailed_error = detailed_error.replace('[sudo] password for ' + username + ': ', '').strip()
                    error_msg = f'设置执行权限失败: {detailed_error}'
                    print(f"设备 {ip} 设置权限失败: {error_msg}")
                    results.append({
                        'ip': ip,
                        'success': False,
                        'message': error_msg
                    })
                    return
                
                # 验证文件是否成功上传并存在
                check_file_cmd = f'echo "{password}" | sudo -S ls -la "{remote_path}"'
                stdin, stdout, stderr = ssh.exec_command(check_file_cmd, get_pty=True)
                file_output = stdout.read().decode()
                file_error = stderr.read().decode()
                print(f"检查文件结果: {file_output}")
                if file_error:
                    print(f"检查文件错误: {file_error}")
                
                # 只有确认文件存在才视为成功
                if script_filename in file_output:
                    results.append({
                        'ip': ip,
                        'success': True,
                        'message': f'脚本已成功部署到 {target_path}'
                    })
                else:
                    error_msg = f'文件部署失败，无法验证文件存在'
                    print(f"设备 {ip} 部署验证失败: {error_msg}")
                    results.append({
                        'ip': ip,
                        'success': False,
                        'message': error_msg
                    })
            finally:
                sftp.close()
                ssh.close()
        except Exception as e:
            error_msg = f'部署脚本过程出现异常: {str(e)}'
            print(f"设备 {ip} 部署脚本异常: {error_msg}")
            results.append({
                'ip': ip,
                'success': False,
                'message': error_msg
            })
    
    # 启动多线程并行部署
    results = []
    threads = []
    
    for device in devices:
        thread = threading.Thread(target=deploy_to_device, args=(device, results))
        thread.start()
        threads.append(thread)
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    return jsonify({
        'success': True,
        'results': results
    })

# 在设备上执行脚本
@scripts_bp.route('/api/knowledge/scripts/execute', methods=['POST'])
@login_required
def execute_script():
    """执行脚本"""
    try:
        data = request.get_json()
        script_path = data.get('scriptPath')
        params = data.get('params', '')
        use_root = data.get('useRoot', False)
        devices = data.get('devices', [])
        
        if not script_path or not devices:
            return jsonify({'success': False, 'message': '缺少必要参数'})
            
        # 获取脚本内容
        script_content = get_script_content(script_path)
        if not script_content:
            return jsonify({'success': False, 'message': '脚本不存在'})
        
        print(f"执行脚本: {script_path}")
        print(f"参数: {params}")
        print(f"使用root: {use_root}")
        print(f"设备数量: {len(devices)}")
            
        # 处理参数中的路径和命令
        commands = []
        if params:
            # 分割参数，处理 cd 命令
            param_parts = params.split('\\')
            for part in param_parts:
                part = part.strip()
                if part and part != '&&':  # 确保不是空部分或单独的&&
                    if part.startswith('cd '):
                        # 将 cd 命令转换为绝对路径
                        path = part[3:].strip()
                        if not path.startswith('/'):
                            path = f"/{path}"
                        commands.append(f"cd {path}")
                    else:
                        commands.append(part)
        
        # 处理脚本内容，确保使用正确的换行符
        script_content = script_content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 线程函数: 在设备上执行脚本
        def execute_on_device(device, results):
            ssh = None
            try:
                # 建立SSH连接
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print(f"正在连接到设备: {device['ip']}:{device['sshPort']}")
                
                try:
                    ssh.connect(
                        hostname=device['ip'],
                        port=device['sshPort'],
                        username=device['username'],
                        password=device['password'],
                        timeout=10
                    )
                    print(f"成功连接到设备: {device['ip']}")
                except Exception as conn_e:
                    error_msg = f'连接失败: {str(conn_e)}'
                    print(f"SSH连接错误: {error_msg}")
                    traceback.print_exc()
                    results.append({
                        'ip': device['ip'],
                        'status': '执行失败',
                        'message': error_msg
                    })
                    return
                
                try:
                    # 使用base64编码脚本内容，避免依赖SFTP
                    import base64
                    encoded_content = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')
                    
                    # 创建临时目录
                    print(f"创建临时目录...")
                    mkdir_cmd = f"echo '{device['password']}' | sudo -S mkdir -p /tmp/scripts && sudo -S chmod 777 /tmp/scripts"
                    stdin, stdout, stderr = ssh.exec_command(mkdir_cmd, get_pty=True, timeout=5)
                    exit_status = stdout.channel.recv_exit_status()
                    
                    # 创建临时脚本文件
                    temp_script = f"/tmp/scripts/script_{int(time.time())}.py"
                    print(f"创建临时脚本: {temp_script}")
                    
                    # 使用echo和base64命令创建脚本
                    write_cmd = f"echo '{encoded_content}' | base64 -d | sudo -S tee {temp_script} > /dev/null && sudo -S chmod 755 {temp_script}"
                    stdin, stdout, stderr = ssh.exec_command(write_cmd, get_pty=True, timeout=5)
                    exit_status = stdout.channel.recv_exit_status()
                    
                    # 验证脚本是否成功创建
                    check_cmd = f"sudo -S ls -la {temp_script}"
                    stdin, stdout, stderr = ssh.exec_command(check_cmd, get_pty=True, timeout=5)
                    check_output = stdout.read().decode('utf-8')
                    check_error = stderr.read().decode('utf-8')
                    print(f"检查脚本: {check_output}")
                    if check_error:
                        print(f"检查错误: {check_error}")
                    
                    # 解析 params 参数为实际的命令序列
                    parsed_commands = []
                    if "&&" in params:
                        parts = params.split("&&")
                        for part in parts:
                            if part.strip():
                                parsed_commands.append(part.strip())
                    else:
                        # 如果没有 && 分隔符，直接添加
                        if params.strip():
                            parsed_commands.append(params.strip())
                    
                    print(f"解析后的命令: {parsed_commands}")
                    
                    # 构建执行命令
                    if use_root:
                        if parsed_commands:
                            # 如果有解析出的命令序列，直接使用这些命令
                            command = '; '.join(parsed_commands)
                            # 在命令的最后位置添加sudo -S python3 {temp_script}
                            command = f"{command}; echo '{device['password']}' | sudo -S python3 {temp_script}"
                        else:
                            # 没有额外命令，直接执行脚本
                            command = f"echo '{device['password']}' | sudo -S python3 {temp_script}"
                    else:
                        if parsed_commands:
                            # 如果有解析出的命令序列，直接使用这些命令
                            command = '; '.join(parsed_commands)
                            # 在命令的最后位置添加python3 {temp_script}
                            command = f"{command}; python3 {temp_script}"
                        else:
                            # 没有额外命令，直接执行脚本
                            command = f"python3 {temp_script}"
                    
                    print(f"最终执行命令: {command}")
                    
                    # 执行命令，设置超时时间
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True, timeout=30)
                    
                    # 使用非阻塞方式读取输出
                    import select
                    channel = stdout.channel
                    output = ""
                    error = ""
                    
                    # 设置超时
                    timeout = 60
                    start_time = time.time()
                    
                    # 非阻塞读取输出
                    while not channel.exit_status_ready():
                        # 检查是否超时
                        if time.time() - start_time > timeout:
                            print(f"执行超时 ({timeout}秒)，强制终止")
                            channel.close()
                            results.append({
                                'ip': device['ip'],
                                'status': '执行失败',
                                'message': f'执行超时 ({timeout}秒)，已强制终止'
                            })
                            return
                            
                        if channel.recv_ready():
                            recv = channel.recv(1024).decode('utf-8', errors='ignore')
                            output += recv
                            print(f"部分输出: {recv}")
                            
                        if channel.recv_stderr_ready():
                            recv_err = channel.recv_stderr(1024).decode('utf-8', errors='ignore')
                            error += recv_err
                            print(f"部分错误: {recv_err}")
                            
                        # 短暂休眠，避免CPU占用过高
                        time.sleep(0.1)
                    
                    # 获取剩余输出
                    while channel.recv_ready():
                        output += channel.recv(1024).decode('utf-8', errors='ignore')
                    while channel.recv_stderr_ready():
                        error += channel.recv_stderr(1024).decode('utf-8', errors='ignore')
                        
                    exit_status = channel.recv_exit_status()
                    print(f"脚本执行完成，退出状态: {exit_status}")
                    
                    # 清理临时文件
                    ssh.exec_command(f"sudo -S rm -f {temp_script}", get_pty=True, timeout=5)
                    
                    # 处理输出结果 - 修改判断逻辑
                    if exit_status != 0:
                        # 退出状态非0，表示执行失败
                        results.append({
                            'ip': device['ip'],
                            'status': '执行失败',
                            'message': f'脚本执行出错 (退出码: {exit_status}): {error or "无详细错误信息"}'
                        })
                    elif error and not error.replace(f"[sudo] password for {device['username']}: ", "").strip() == "":
                        # 有错误输出但退出状态为0，可能是警告信息
                        clean_error = error.replace(f"[sudo] password for {device['username']}: ", "")
                        results.append({
                            'ip': device['ip'],
                            'status': '执行成功',
                            'message': f'脚本执行成功，但有警告信息: {clean_error}\n\n输出信息: {output}'
                        })
                    else:
                        # 正常执行完成
                        results.append({
                            'ip': device['ip'],
                            'status': '执行成功',
                            'message': output or "脚本执行成功，无输出信息"
                        })
                        
                except Exception as e:
                    error_msg = f'执行脚本失败: {str(e) or "未知错误"}'
                    print(f"执行脚本错误: {error_msg}")
                    traceback.print_exc()
                    results.append({
                        'ip': device['ip'],
                        'status': '执行失败',
                        'message': error_msg
                    })
            except Exception as e:
                tb = traceback.format_exc()
                error_msg = f'连接或执行过程出错: {str(e) or "未知错误"}'
                print(f"总体错误: {error_msg}")
                print(f"错误详情: {tb}")
                results.append({
                    'ip': device['ip'],
                    'status': '执行失败',
                    'message': error_msg
                })
            finally:
                # 确保SSH连接被关闭
                if ssh:
                    try:
                        ssh.close()
                    except:
                        pass
        
        # 启动多线程执行
        results = []
        threads = []
        
        for device in devices:
            thread = threading.Thread(target=execute_on_device, args=(device, results))
            thread.daemon = True  # 设置为守护线程，主线程结束时自动结束
            thread.start()
            threads.append(thread)
        
        # 等待所有线程完成，最多等待120秒
        max_wait_time = 120
        start_time = time.time()
        for thread in threads:
            remaining_time = max_wait_time - (time.time() - start_time)
            if remaining_time <= 0:
                break
            thread.join(remaining_time)
            
        # 检查是否所有线程都已完成
        active_threads = [t for t in threads if t.is_alive()]
        if active_threads:
            print(f"有 {len(active_threads)} 个设备执行超时")
            # 添加超时设备的结果
            for device in devices:
                if not any(r.get('ip') == device['ip'] for r in results):
                    results.append({
                        'ip': device['ip'],
                        'status': '执行失败',
                        'message': '执行超时，可能是脚本无响应或正在持续运行'
                    })
                
        return jsonify({
            'success': True,
            'message': '执行完成',
            'results': results
        })
        
    except Exception as e:
        print(f"执行失败: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'执行失败: {str(e)}'
        })

# 获取所有目录列表
@scripts_bp.route('/api/scripts/list_all_directories', methods=['GET'])
@login_required
def list_all_directories():
    try:
        # 基础目录就是scripts目录
        base_dir = os.path.join(SCRIPTS_ROOT, 'scripts')
        # 保存所有目录的列表
        all_directories = ['/scripts']  # 确保根目录存在
        
        # 递归扫描脚本根目录下的所有子目录
        def scan_directories(fs_path, web_path='/scripts'):
            if not os.path.exists(fs_path) or not os.path.isdir(fs_path):
                return
                
            try:
                items = os.listdir(fs_path)
            except OSError as e:
                print(f"无法读取目录 {fs_path}: {e}")
                return

            for item in items:
                item_fs_path = os.path.join(fs_path, item)
                if os.path.isdir(item_fs_path):
                    # 构建子目录的Web路径
                    item_web_path = f"{web_path}/{item}"
                    # 清理并添加到目录列表
                    clean_web_path = clean_path(item_web_path)
                    
                    if clean_web_path not in all_directories:
                        print(f"添加目录: {clean_web_path}")
                        all_directories.append(clean_web_path)
                    
                    # 递归扫描子目录
                    scan_directories(item_fs_path, item_web_path)
        
        # 扫描scripts目录下的所有子目录
        scan_directories(base_dir)
            
        # 排序并返回目录列表
        all_directories.sort()
        
        print(f"找到 {len(all_directories)} 个目录: {all_directories}")
        
        return jsonify({
            'success': True, 
            'directories': all_directories
        })
    except Exception as e:
        print(f"获取目录列表出错: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'message': f'获取目录列表失败: {str(e)}',
            'directories': ['/scripts']  # 至少返回根目录
        })

# 新的上传处理函数，处理路径格式问题
@scripts_bp.route('/api/scripts/handle_upload', methods=['POST'])
@login_required
def handle_upload():
    try:
        upload_dir = request.form.get('uploadDirectory', '')
        print(f"原始上传目录路径: {upload_dir}")
        
        if not upload_dir:
            upload_dir = '/scripts'
        
        # 使用统一的路径清理函数
        upload_dir = clean_path(upload_dir)
        print(f"清理后的上传目录: {upload_dir}")
        
        if 'scriptFile' not in request.files:
            return jsonify({'success': False, 'message': '没有找到上传的文件'}), 400
        
        script_file = request.files['scriptFile']
        original_filename = script_file.filename
        print(f"上传文件: {original_filename}")
        
        if not original_filename:
            return jsonify({'success': False, 'message': '未选择文件'}), 400
        
        # 更严格地清理文件名，确保没有控制字符
        clean_filename = re.sub(r'[\x00-\x1f\x7f-\x9f<>:"/\\|?*]', '', original_filename)
        if not clean_filename:
            return jsonify({'success': False, 'message': '文件名无效，包含不支持的字符'}), 400
        
        filename = secure_filename(clean_filename)
        print(f"清理后的文件名: {filename}")
        
        # 检查文件扩展名
        allowed_extensions = ['.sh', '.py', '.bat', '.cmd', '.ps1']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'success': False, 'message': f'文件类型不允许，只支持以下类型: {", ".join(allowed_extensions)}'}), 400
        
        # 使用新的路径转换函数获取文件系统路径
        base_dir = web_to_fs_path(upload_dir)
        print(f"转换后的文件系统路径: {base_dir}")
        
        # 确保目录存在
        if not os.path.exists(base_dir):
            print(f"创建目录: {base_dir}")
            os.makedirs(base_dir, exist_ok=True)
        
        if not os.path.isdir(base_dir):
            return jsonify({'success': False, 'message': '上传目录不是一个有效的目录'}), 400
        
        # 构建保存文件的完整路径
        file_path = os.path.join(base_dir, filename)
        print(f"文件将保存到: {file_path}")
        
        # 保存文件
        try:
            script_file.save(file_path)
            
            # 为脚本文件添加执行权限(Linux/Unix)
            if os.name != 'nt':
                os.chmod(file_path, 0o755)
            
            print(f"文件上传成功: {file_path}")
            
            # 返回成功的同时，告诉前端正确的目录路径，以便刷新显示
            return jsonify({
                'success': True, 
                'message': '文件上传成功',
                'directory': upload_dir
            })
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'保存文件失败: {str(e)}'}), 500
    except Exception as e:
        print(f"上传处理出错: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'上传脚本出错: {str(e)}'}), 500

@scripts_bp.route('/api/scripts/ssh_connect', methods=['POST'])
def ssh_connect():
    """启动SSH连接到指定设备，自动处理首次连接确认和密码输入"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "请求数据无效"}), 400
        
        # 检查必要参数
        ip = data.get('ip')
        port = data.get('port', 22)
        username = data.get('username')
        password = data.get('password')
        
        if not all([ip, username, password]):
            return jsonify({"success": False, "message": "缺少必要的连接参数"}), 400
        
        # 在Windows环境下，创建一个PowerShell脚本来自动处理SSH连接
        import tempfile
        import os
        import subprocess

        # 创建临时PowerShell脚本文件
        fd, ps_script = tempfile.mkstemp(suffix='.ps1')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write('# PowerShell脚本用于自动处理SSH连接和密码输入\n')
                f.write(f'Write-Host "正在自动连接到 {username}@{ip}:{port}..."\n')
                f.write(f'Write-Host "系统将自动输入yes确认和密码"\n\n')
                
                # 使用StrictHostKeyChecking=no选项自动接受主机密钥
                f.write(f'$sshCommand = "ssh {username}@{ip} -p {port} -o StrictHostKeyChecking=no"\n')
                f.write('$psi = New-Object System.Diagnostics.ProcessStartInfo\n')
                f.write('$psi.FileName = "cmd.exe"\n')
                f.write('$psi.Arguments = "/k $sshCommand"\n')
                f.write('$psi.UseShellExecute = $true\n')
                f.write('[System.Diagnostics.Process]::Start($psi)\n')
                
                # 等待并显示密码信息
                f.write('Start-Sleep -Seconds 2\n')
                f.write('$wshell = New-Object -ComObject wscript.shell\n')
                f.write('$wshell.AppActivate("cmd.exe")\n')
                f.write('Start-Sleep -Seconds 1\n')
                f.write(f'Write-Host "-------------------------------------------------"\n')
                f.write(f'Write-Host "已自动处理yes确认。请在看到密码提示时输入以下密码:"\n')
                f.write(f'Write-Host "{password}"\n')
                f.write(f'Write-Host "-------------------------------------------------"\n')
                f.write(f'# 自动将密码复制到剪贴板以方便用户粘贴\n')
                f.write(f'Set-Clipboard -Value "{password}"\n')
                f.write(f'Write-Host "密码已复制到剪贴板，您可以直接按Ctrl+V粘贴"\n')
                
            # 使用PowerShell启动脚本
            ps_cmd = f'powershell.exe -ExecutionPolicy Bypass -File "{ps_script}"'
            subprocess.Popen(ps_cmd, shell=True)
            
            # 等待一段时间后删除临时脚本
            import threading
            def delete_script():
                import time
                time.sleep(10)  # 10秒后删除文件
                try:
                    os.remove(ps_script)
                except:
                    pass
            
            threading.Thread(target=delete_script).start()
            
            return jsonify({
                "success": True,
                "message": f"正在连接到 {username}@{ip}:{port}，系统将自动处理确认，并已将密码复制到剪贴板"
            })
            
        except Exception as e:
            # 如果出错，尝试删除临时文件
            try:
                os.remove(ps_script)
            except:
                pass
            print(f"SSH连接错误: {str(e)}")
            # 使用简单方式连接
            subprocess.Popen(f'start cmd.exe /K "ssh {username}@{ip} -p {port} -o StrictHostKeyChecking=no"', shell=True)
            return jsonify({
                "success": True,
                "message": f"已启动SSH连接到 {username}@{ip}:{port}，已禁用主机验证，请手动输入密码"
            })
            
    except Exception as e:
        print(f"SSH连接错误: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"SSH连接失败: {str(e)}"
        }), 500 

def get_script_content(script_path):
    """获取脚本内容"""
    try:
        # 规范化路径
        if script_path.startswith('/scripts/'):
            script_path = script_path[9:]  # 去掉/scripts/前缀
        elif script_path.startswith('/scripts'):
            script_path = script_path[8:]  # 去掉/scripts前缀
        elif script_path.startswith('scripts/'):
            script_path = script_path[8:]  # 去掉scripts/前缀
            
        # 构建完整路径
        full_path = os.path.join(SCRIPTS_ROOT, 'scripts', script_path)
        print(f"尝试读取脚本: {full_path}")
        
        # 检查文件是否存在
        if not os.path.exists(full_path):
            print(f"脚本文件不存在: {full_path}")
            return None
            
        # 读取文件内容
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"成功读取脚本内容，大小: {len(content)} 字节")
            return content
            
    except Exception as e:
        print(f"读取脚本内容失败: {str(e)}")
        return None 