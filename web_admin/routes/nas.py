from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
import requests

nas = Blueprint('nas', __name__)

@nas.route('/nas_finder')
@login_required
def nas_finder():
    """渲染 NAS 设备搜索页面"""
    # 从 JSON 文件加载问题和答案
    from flask_login import current_user
    from flask import current_app
    import os, json
    
    questions_file = os.path.join(current_app.root_path, 'nas_devices', 'questions.json')
    
    # 默认值
    storage_question = "请输入存储组访问密码:"
    performance_question = "请输入性能专项组访问密码:"
    storage_name = "存储组"
    performance_name = "性能专项组"
    
    if os.path.exists(questions_file):
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            storage_question = questions.get('storage', {}).get('question', storage_question)
            performance_question = questions.get('performance', {}).get('question', performance_question)
            storage_name = questions.get('storage', {}).get('name', storage_name)
            performance_name = questions.get('performance', {}).get('name', performance_name)
    
    return render_template('nas_finder.html',
                        storage_question=storage_question,
                        performance_question=performance_question,
                        storage_name=storage_name,
                        performance_name=performance_name,
                        is_admin=current_user.is_admin())

@nas.route('/api/pointer_search', methods=['POST'])
def pointer_search():
    try:
        data = request.get_json()
        network_segments = data.get('networkSegments', [])
        device_name = data.get('deviceName', '')
        device_model = data.get('deviceModel', '')
        use_client_ip = data.get('clientIp', False)

        # 如果使用客户端IP
        if use_client_ip:
            client_ip = request.remote_addr
            # 如果使用了代理，尝试获取真实IP
            if request.headers.get('X-Forwarded-For'):
                client_ip = request.headers.get('X-Forwarded-For').split(',')[0]
            # 获取客户端IP的网段
            client_network = '.'.join(client_ip.split('.')[:3])
            if client_network not in network_segments:
                network_segments.append(client_network)

        # 执行设备搜索
        devices = []
        for segment in network_segments:
            # 对每个网段执行搜索
            segment_devices = search_devices_in_segment(segment, device_name, device_model)
            devices.extend(segment_devices)

        return jsonify({'devices': devices})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def search_devices_in_segment(segment, device_name=None, device_model=None):
    """
    在指定网段搜索设备
    """
    devices = []
    # 遍历网段中的所有IP
    for i in range(1, 255):
        ip = f"{segment}.{i}"
        try:
            # 使用asyncio进行并发请求
            device = check_device(ip)
            if device:
                # 如果指定了设备名称或型号，进行过滤
                if device_name and device_name.lower() not in device['name'].lower():
                    continue
                if device_model and device_model.lower() not in device.get('model', '').lower():
                    continue
                devices.append(device)
        except Exception as e:
            continue
    return devices

def check_device(ip):
    """
    检查指定IP是否为目标设备
    """
    try:
        # 首先尝试HTTP
        response = requests.get(f"http://{ip}:9999/system/check", timeout=0.5)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                return {
                    'name': data['data'].get('device_name', 'Unknown'),
                    'model': data['data'].get('model', ''),
                    'ipv4': ip
                }
    except:
        try:
            # 如果HTTP失败，尝试HTTPS
            response = requests.get(f"https://{ip}:9443/system/check", 
                                 timeout=0.5, 
                                 verify=False)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    return {
                        'name': data['data'].get('device_name', 'Unknown'),
                        'model': data['data'].get('model', ''),
                        'ipv4': ip
                    }
        except:
            pass
    return None 