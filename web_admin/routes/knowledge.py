from flask import Blueprint, render_template, request, jsonify, current_app, send_file, send_from_directory, session as flask_session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from functools import wraps
import logging
import time
import hashlib
import requests

# 创建蓝图
knowledge = Blueprint('knowledge', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': '权限不足，需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

@knowledge.route('/knowledge-base')
@login_required
def knowledge_base():
    """渲染知识库主页"""
    try:
        # 确保知识库目录存在
        kb_path = current_app.config.get('KNOWLEDGE_BASE_PATH')
        if not kb_path:
            kb_path = os.path.join(current_app.root_path, 'data', 'knowledge_base')
            current_app.config['KNOWLEDGE_BASE_PATH'] = kb_path
        
        os.makedirs(kb_path, exist_ok=True)
        
        # 始终使用新版模板
        template = 'knowledge_base_new.html'
        
        return render_template(template, 
                             current_user=current_user, 
                             is_admin=current_user.is_admin)
    except Exception as e:
        current_app.logger.error(f"渲染知识库页面时出错: {str(e)}", exc_info=True)
        return render_template('knowledge_base_new.html', 
                             current_user=current_user,
                             is_admin=current_user.is_admin)

@knowledge.route('/api/knowledge/modules', methods=['GET'])
@login_required
def get_modules():
    """获取所有模块"""
    try:
        # 确保知识库目录存在
        kb_path = current_app.config.get('KNOWLEDGE_BASE_PATH')
        if not kb_path:
            kb_path = os.path.join(current_app.root_path, 'data', 'knowledge_base')
            current_app.config['KNOWLEDGE_BASE_PATH'] = kb_path
            
        os.makedirs(kb_path, exist_ok=True)
        
        # 确保articles目录存在
        articles_path = os.path.join(kb_path, 'articles')
        os.makedirs(articles_path, exist_ok=True)
        
        # 获取模块配置文件路径
        config_path = os.path.join(kb_path, 'modules.json')
        current_app.logger.info(f'获取模块，配置文件路径: {config_path}')
        
        # 读取模块配置
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    modules = json.load(f)
                current_app.logger.info(f'已加载模块列表，共{len(modules)}个')
                
                # 确保modules是列表类型
                if not isinstance(modules, list):
                    current_app.logger.warning(f'模块数据格式不正确，重置为空列表: {type(modules)}')
                    modules = []
            except Exception as e:
                current_app.logger.error(f'读取模块配置失败: {str(e)}')
                modules = []
        else:
            current_app.logger.info('模块配置文件不存在，返回空列表')
            modules = []
        
        # 更新模块ID（确保稳定性）
        def update_module_ids(modules_list):
            for module in modules_list:
                if 'id' not in module or not module['id']:
                    module['id'] = f"module_{int(datetime.now().timestamp())}"
                if 'children' in module and module['children']:
                    update_module_ids(module['children'])
        
        # 更新每个模块的文章计数
        def count_json_files(directory):
            try:
                if not os.path.exists(directory):
                    return 0
                return len([f for f in os.listdir(directory) if f.endswith('.json')])
            except Exception as e:
                current_app.logger.error(f'计算文章数量失败: {str(e)}')
                return 0
        
        def update_module_count(module_list):
            for module in module_list:
                module_dir = os.path.join(articles_path, module['id'])
                module['count'] = count_json_files(module_dir)
                if 'children' in module and module['children']:
                    update_module_count(module['children'])
        
        # 更新模块ID和计数
        update_module_ids(modules)
        update_module_count(modules)
        
        # 保存更新后的模块配置
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(modules, f, ensure_ascii=False, indent=2)
            current_app.logger.info('已保存更新后的模块配置')
        except Exception as e:
            current_app.logger.error(f'保存模块配置失败: {str(e)}')
        
        return jsonify({
            'success': True,
            'modules': modules
        })
    except Exception as e:
        current_app.logger.error(f'获取模块列表失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e),
            'modules': []
        })

@knowledge.route('/api/knowledge/module-tree', methods=['GET'])
@login_required
@admin_required
def get_module_tree():
    """获取模块树结构（仅管理员可见）"""
    try:
        modules_file = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'modules.json')
        if os.path.exists(modules_file):
            with open(modules_file, 'r', encoding='utf-8') as f:
                modules = json.load(f)
        else:
            return jsonify({'error': '模块配置文件不存在'}), 404
        return jsonify(modules)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/save', methods=['POST'])
@login_required
@admin_required
def save_article():
    """保存知识文档（仅管理员可用）"""
    try:
        title = request.form.get('title')
        module = request.form.get('module')
        content = request.form.get('content')
        
        if not title or not module:
            return jsonify({'error': '缺少必要参数'}), 400
            
        # 生成文章ID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        article_id = f"a_{timestamp}"
        
        # 创建文章目录
        article_dir = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'articles', module)
        os.makedirs(article_dir, exist_ok=True)
        
        # 保存文章信息
        article_data = {
            'id': article_id,
            'title': title,
            'module': module,
            'content': content or f"# {title}\n\n请在这里编写文章内容",
            'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'author': current_user.username,
            'status': 'published'
        }
        
        article_file = os.path.join(article_dir, f'{article_id}.json')
        
        with open(article_file, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=4)
            
        return jsonify({
            'success': True, 
            'article': article_data,
            'message': '文档保存成功'
        })
    except Exception as e:
        logging.error(f"保存文章失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/search', methods=['POST'])
@login_required
def search_knowledge():
    """搜索知识库内容"""
    try:
        data = request.get_json()
        if not data:
            data = request.form.to_dict()
            
        keyword = data.get('keyword', '')
        
        current_app.logger.info(f"搜索知识库，关键词: {keyword}")
        
        if not keyword:
            return jsonify({'success': False, 'message': '搜索关键词不能为空'}), 400
            
        articles = []
        
        # 确保知识库目录存在
        kb_path = current_app.config.get('KNOWLEDGE_BASE_PATH')
        if not kb_path:
            kb_path = os.path.join(current_app.root_path, 'data', 'knowledge_base')
            current_app.config['KNOWLEDGE_BASE_PATH'] = kb_path
            
        os.makedirs(kb_path, exist_ok=True)
        
        # 确保articles目录存在
        articles_dir = os.path.join(kb_path, 'articles')
        os.makedirs(articles_dir, exist_ok=True)
        
        # 加载模块配置，用于获取模块名称
        modules_file = os.path.join(kb_path, 'modules.json')
        modules_map = {}  # 用于存储模块ID和名称的映射
        
        if os.path.exists(modules_file):
            try:
                with open(modules_file, 'r', encoding='utf-8') as f:
                    modules_data = json.load(f)
                    
                # 创建模块ID到名称的映射
                def build_module_map(modules_list):
                    for module in modules_list:
                        if isinstance(module, dict) and 'id' in module and 'name' in module:
                            modules_map[module['id']] = module['name']
                            
                        # 递归处理子模块
                        if isinstance(module, dict) and 'children' in module and isinstance(module['children'], list):
                            build_module_map(module['children'])
                            
                # 构建模块映射
                if isinstance(modules_data, list):
                    build_module_map(modules_data)
            except Exception as e:
                current_app.logger.error(f"加载模块配置失败: {e}")
        
        # 遍历所有模块目录
        for module_id in os.listdir(articles_dir):
            module_dir = os.path.join(articles_dir, module_id)
            if not os.path.isdir(module_dir):
                continue
                
            # 获取模块名称
            module_name = modules_map.get(module_id, module_id)
            
            # 遍历模块下的所有文章
            for article_file in os.listdir(module_dir):
                if not article_file.endswith('.json'):
                    continue
                    
                article_path = os.path.join(module_dir, article_file)
                
                try:
                    with open(article_path, 'r', encoding='utf-8') as f:
                        article_data = json.load(f)
                        
                    # 确保article_data是字典类型
                    if not isinstance(article_data, dict):
                        current_app.logger.warning(f"文章数据格式错误: {article_path}")
                        continue
                        
                    # 获取文章ID（从文件名或数据中）
                    article_id = article_data.get('id')
                    if not article_id:
                        article_id = os.path.splitext(article_file)[0]
                        
                    # 获取文章标题、内容等信息
                    title = article_data.get('title', '无标题')
                    content = article_data.get('content', '')
                    
                    # 向下兼容旧版格式
                    if not content and 'html' in article_data:
                        content = article_data.get('html', '')
                        
                    # 获取创建时间和更新时间
                    created_at = article_data.get('created_at') or article_data.get('create_time', '')
                    updated_at = article_data.get('updated_at') or article_data.get('update_time', '')
                    
                    # 应用关键词过滤
                    if keyword.lower() not in title.lower() and keyword.lower() not in content.lower():
                        continue
                    
                    # 添加到搜索结果
                    articles.append({
                        'id': article_id,
                        'title': title,
                        'module': module_name,
                        'module_id': module_id,
                        'created_at': created_at,
                        'updated_at': updated_at,
                        'created_by': article_data.get('created_by', '') or article_data.get('author', ''),
                        'updated_by': article_data.get('updated_by', '') or article_data.get('author', ''),
                        # 不包含完整内容，避免返回数据过大
                        'summary': content[:200] + ('...' if len(content) > 200 else '')
                    })
                except Exception as e:
                    current_app.logger.error(f"读取文章文件失败: {article_path}, 错误: {e}")
        
        # 按更新时间排序（最新的优先）
        articles.sort(key=lambda x: x.get('updated_at', '') or x.get('created_at', ''), reverse=True)
        
        current_app.logger.info(f"搜索完成，找到 {len(articles)} 个结果")
        return jsonify({'success': True, 'articles': articles})
    except Exception as e:
        error_message = f"搜索知识库失败: {str(e)}"
        current_app.logger.error(error_message, exc_info=True)
        return jsonify({'success': False, 'error': error_message}), 500

@knowledge.route('/api/knowledge/article/<article_id>', methods=['GET'])
@login_required
def get_article(article_id):
    """获取文章详情"""
    try:
        current_app.logger.info(f"获取文章: {article_id}")
        
        # 确保知识库目录存在
        kb_path = current_app.config.get('KNOWLEDGE_BASE_PATH')
        if not kb_path:
            kb_path = os.path.join(current_app.root_path, 'data', 'knowledge_base')
            current_app.config['KNOWLEDGE_BASE_PATH'] = kb_path
            
        # 确保articles目录存在
        articles_dir = os.path.join(kb_path, 'articles')
        os.makedirs(articles_dir, exist_ok=True)
        
        # 遍历所有模块目录查找文章
        article_found = False
        error_messages = []
        
        try:
            for module in os.listdir(articles_dir):
                module_dir = os.path.join(articles_dir, module)
                if not os.path.isdir(module_dir):
                    continue
                    
                article_file = os.path.join(module_dir, f'{article_id}.json')
                if os.path.exists(article_file):
                    article_found = True
                    current_app.logger.info(f"找到文章文件: {article_file}")
                    
                    try:
                        with open(article_file, 'r', encoding='utf-8') as f:
                            article = json.load(f)
                            
                        # 直接返回文章内容，不要嵌套在article字段中
                        return jsonify({
                            'success': True,
                            'id': article_id,
                            'content': article.get('content', ''),
                            'title': article.get('title', '无标题'),
                            'module_id': article.get('module_id', module),  # 如果没有module_id，使用文件夹名称
                            'created_at': article.get('created_at', ''),
                            'updated_at': article.get('updated_at', ''),
                            'created_by': article.get('created_by', ''),
                            'updated_by': article.get('updated_by', '')
                        })
                    except Exception as e:
                        error_message = f"读取文章文件失败: {str(e)}"
                        current_app.logger.error(error_message)
                        error_messages.append(error_message)
        except Exception as e:
            error_message = f"遍历文章目录失败: {str(e)}"
            current_app.logger.error(error_message)
            error_messages.append(error_message)
                
        if article_found and error_messages:
            # 文章存在但读取失败
            return jsonify({
                'success': False, 
                'error': '文章文件存在但读取失败', 
                'details': error_messages
            }), 500
        else:
            # 文章不存在
            current_app.logger.error(f"文章不存在: {article_id}")
            return jsonify({'success': False, 'error': '文章不存在'}), 404
    except Exception as e:
        current_app.logger.error(f"获取文章失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': f"获取文章失败: {str(e)}"}), 500

@knowledge.route('/api/knowledge/article/<article_id>/attachment/<filename>')
@login_required
def get_attachment(article_id, filename):
    """下载文章附件"""
    try:
        # 遍历所有模块目录查找附件
        articles_dir = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'articles')
        for module in os.listdir(articles_dir):
            attachment_path = os.path.join(articles_dir, module, article_id, secure_filename(filename))
            if os.path.exists(attachment_path):
                return send_file(attachment_path)
                
        return jsonify({'error': '附件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/article/<article_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_article(article_id):
    """删除文章（仅管理员可用）"""
    try:
        # 遍历所有模块目录查找文章
        articles_dir = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'articles')
        module_id = None  # 用于记录文章所属的模块ID
        
        for module in os.listdir(articles_dir):
            article_file = os.path.join(articles_dir, module, f'{article_id}.json')
            if os.path.exists(article_file):
                # 获取文章信息，以便返回模块ID
                with open(article_file, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                module_id = article.get('module_id', module)
                
                # 删除文章文件
                os.remove(article_file)
                
                # 删除附件目录
                attachment_dir = os.path.join(articles_dir, module, article_id)
                if os.path.exists(attachment_dir):
                    for file in os.listdir(attachment_dir):
                        os.remove(os.path.join(attachment_dir, file))
                    os.rmdir(attachment_dir)
                
                # 从模块配置中移除文章引用
                if module_id:
                    modules_file = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'modules.json')
                    if os.path.exists(modules_file):
                        try:
                            with open(modules_file, 'r', encoding='utf-8') as f:
                                modules_data = json.load(f)
                            
                            # 确保modules_data是正确的格式
                            if isinstance(modules_data, dict) and 'modules' in modules_data:
                                modules = modules_data['modules']
                            elif isinstance(modules_data, list):
                                modules = modules_data
                            else:
                                modules = []

                            # 递归查找并移除文章引用
                            def remove_article_from_module(modules_list, target_module_id, article_id):
                                for module in modules_list:
                                    if not isinstance(module, dict):
                                        continue
                                        
                                    if module.get('id') == target_module_id:
                                        # 移除文章引用
                                        if 'articles' in module and isinstance(module['articles'], list):
                                            module['articles'] = [a for a in module['articles'] if not (isinstance(a, dict) and a.get('id') == article_id)]
                                        return True
                                    
                                    # 递归检查子模块
                                    if 'children' in module and isinstance(module['children'], list):
                                        if remove_article_from_module(module['children'], target_module_id, article_id):
                                            return True
                                return False
                            
                            # 执行文章移除
                            remove_article_from_module(modules, module_id, article_id)
                            
                            # 保存更新后的模块配置
                            with open(modules_file, 'w', encoding='utf-8') as f:
                                json.dump(modules, f, ensure_ascii=False, indent=2)
                            
                            current_app.logger.info(f"从模块 {module_id} 中移除文章 {article_id} 的引用")
                        except Exception as e:
                            current_app.logger.error(f"更新模块配置失败: {str(e)}")
                
                return jsonify({
                    'success': True,
                    'module_id': module_id,
                    'message': '文章删除成功'
                })
        
        # 如果没有找到文章
        return jsonify({
            'success': False,
            'message': '文章不存在'
        }), 404
    except Exception as e:
        current_app.logger.error(f"删除文章失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'删除文章失败: {str(e)}'
        }), 500

@knowledge.route('/api/knowledge/module', methods=['POST'])
@login_required
@admin_required
def add_module():
    """添加新模块（仅管理员可用）"""
    try:
        data = request.get_json()
        name = data.get('name')
        parent_id = data.get('parent_id')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'success': False, 'message': '模块名称不能为空'}), 400
            
        # 确保知识库目录存在
        kb_path = current_app.config.get('KNOWLEDGE_BASE_PATH')
        if not kb_path:
            kb_path = os.path.join(current_app.root_path, 'data', 'knowledge_base')
            current_app.config['KNOWLEDGE_BASE_PATH'] = kb_path
            
        os.makedirs(kb_path, exist_ok=True)
        
        # 确保articles目录存在
        articles_path = os.path.join(kb_path, 'articles')
        os.makedirs(articles_path, exist_ok=True)
        
        # 获取模块配置文件路径
        config_path = os.path.join(kb_path, 'modules.json')
        current_app.logger.info(f'添加模块，配置文件路径: {config_path}')
        
        # 读取现有模块配置
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    modules = json.load(f)
                # 确保modules是列表类型
                if not isinstance(modules, list):
                    current_app.logger.warning(f'模块数据格式不正确，重置为空列表: {type(modules)}')
                    modules = []
            except Exception as e:
                current_app.logger.error(f'读取模块配置失败: {str(e)}')
                modules = []
        else:
            current_app.logger.info('模块配置文件不存在，创建新的空列表')
            modules = []
        
        # 生成模块ID
        module_id = f"module_{int(datetime.now().timestamp())}"
        
        # 创建新模块
        new_module = {
            'id': module_id,
            'name': name,
            'description': description,
            'articles': [],
            'children': []
        }
        
        # 添加父模块ID（如果有）
        if parent_id:
            new_module['parent_id'] = parent_id
            
            # 添加为子模块
            def add_to_parent(modules_list):
                for module in modules_list:
                    if module['id'] == parent_id:
                        if 'children' not in module:
                            module['children'] = []
                        module['children'].append(new_module)
                        return True
                    if 'children' in module and module['children']:
                        if add_to_parent(module['children']):
                            return True
                return False
            
            if not add_to_parent(modules):
                return jsonify({'success': False, 'message': '父模块不存在'}), 404
        else:
            # 添加为顶级模块
            modules.append(new_module)
        
        # 创建模块目录
        module_dir = os.path.join(articles_path, module_id)
        os.makedirs(module_dir, exist_ok=True)
        
        # 保存更新后的模块配置
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(modules, f, ensure_ascii=False, indent=2)
            current_app.logger.info(f'模块添加成功: {name} (ID: {module_id})')
        except Exception as e:
            current_app.logger.error(f'保存模块配置失败: {str(e)}')
            return jsonify({'success': False, 'message': f'保存模块配置失败: {str(e)}'}), 500
            
        return jsonify({
            'success': True,
            'module': new_module,
            'message': '模块添加成功'
        })
    except Exception as e:
        current_app.logger.error(f'添加模块失败: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'添加模块失败: {str(e)}'}), 500

@knowledge.route('/api/knowledge/module/<module_id>', methods=['DELETE', 'HEAD'])
@login_required
@admin_required
def delete_module(module_id):
    """删除模块（仅管理员可用）"""
    try:
        # 如果是HEAD请求，直接返回成功
        if request.method == 'HEAD':
            return '', 200
            
        modules_file = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'modules.json')
        if not os.path.exists(modules_file):
            return jsonify({'error': '模块配置文件不存在'}), 404
            
        with open(modules_file, 'r', encoding='utf-8') as f:
            modules_data = json.load(f)
            
        # 确保modules_data是正确的格式
        if isinstance(modules_data, dict) and 'modules' in modules_data:
            modules = modules_data['modules']
        elif isinstance(modules_data, list):
            modules = modules_data
        else:
            modules = []
            
        # 删除模块（递归删除子模块）
        def remove_module(modules_list, target_id):
            if not isinstance(modules_list, list):
                return False
                
            for i in range(len(modules_list)):
                module = modules_list[i]
                if not isinstance(module, dict):
                    continue
                    
                if module.get('id') == target_id:
                    # 删除模块目录及其内容
                    module_dir = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'articles', target_id)
                    if os.path.exists(module_dir):
                        for root, dirs, files in os.walk(module_dir, topdown=False):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))
                        os.rmdir(module_dir)
                    
                    # 递归删除子模块
                    if 'children' in module and isinstance(module['children'], list):
                        for child in module['children']:
                            if isinstance(child, dict) and 'id' in child:
                                remove_module(module['children'], child['id'])
                    
                    del modules_list[i]
                    return True
                elif 'children' in module and isinstance(module['children'], list):
                    if remove_module(module['children'], target_id):
                        return True
            return False
            
        if not remove_module(modules, module_id):
            return jsonify({'error': '模块不存在'}), 404
            
        # 保存更新后的模块配置
        with open(modules_file, 'w', encoding='utf-8') as f:
            if isinstance(modules_data, dict):
                modules_data['modules'] = modules
                json.dump(modules_data, f, ensure_ascii=False, indent=4)
            else:
                json.dump(modules, f, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True, 'message': '模块删除成功'})
    except Exception as e:
        current_app.logger.error(f"删除模块时出错: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/module/<module_id>', methods=['GET'])
@login_required
def get_module(module_id):
    """获取单个模块信息"""
    try:
        logging.info(f"正在获取模块信息: {module_id}")
        current_app.logger.info(f"正在获取模块信息: {module_id}")
        
        # 确保知识库目录存在
        kb_path = current_app.config.get('KNOWLEDGE_BASE_PATH')
        if not kb_path:
            kb_path = os.path.join(current_app.root_path, 'data', 'knowledge_base')
            current_app.config['KNOWLEDGE_BASE_PATH'] = kb_path
            
        os.makedirs(kb_path, exist_ok=True)
        
        # 确保articles目录存在
        articles_path = os.path.join(kb_path, 'articles')
        os.makedirs(articles_path, exist_ok=True)
        
        # 获取模块配置文件路径
        modules_file = os.path.join(kb_path, 'modules.json')
        current_app.logger.info(f"模块配置文件路径: {modules_file}")
        
        if not os.path.exists(modules_file):
            current_app.logger.error(f"模块配置文件不存在: {modules_file}")
            return jsonify({'success': False, 'error': '模块配置文件不存在'}), 404
            
        # 读取模块列表
        try:
            with open(modules_file, 'r', encoding='utf-8') as f:
                modules_data = json.load(f)
                current_app.logger.debug("已加载模块配置文件")
            
            # 兼容旧版和新版数据结构
            if isinstance(modules_data, dict) and 'modules' in modules_data:
                modules = modules_data['modules']
            elif isinstance(modules_data, list):
                modules = modules_data
            else:
                modules = []
                current_app.logger.warning(f"模块数据格式不正确: {type(modules_data)}")
        except Exception as e:
            current_app.logger.error(f"读取模块配置失败: {str(e)}")
            return jsonify({'success': False, 'error': f'读取模块配置失败: {str(e)}'}), 500
            
        # 在模块树中查找目标模块
        def find_module(modules_list, target_id):
            for module in modules_list:
                if module.get('id') == target_id:
                    return module
                if 'children' in module and isinstance(module['children'], list):
                    result = find_module(module['children'], target_id)
                    if result:
                        return result
            return None
            
        module = find_module(modules, module_id)
        if not module:
            # 为了调试目的，返回所有模块ID
            all_ids = []
            def collect_ids(modules_list):
                for m in modules_list:
                    all_ids.append(m.get('id', 'unknown'))
                    if 'children' in m and isinstance(m['children'], list):
                        collect_ids(m['children'])
            
            collect_ids(modules)
            current_app.logger.error(f"未找到模块: {module_id}, 可用的模块ID: {all_ids}")
            return jsonify({'success': False, 'error': '模块不存在', 'available_ids': all_ids}), 404
            
        # 确保模块有基本属性
        if 'name' not in module:
            module['name'] = f"模块 {module_id}"
        if 'count' not in module:
            module['count'] = 0
        
        # 获取模块下的所有文章
        articles = []
        module_dir = os.path.join(articles_path, module_id)
        current_app.logger.info(f"查找模块文章目录: {module_dir}")
        
        if os.path.exists(module_dir):
            current_app.logger.info(f"模块目录存在，查找文章...")
            try:
                files = os.listdir(module_dir)
                current_app.logger.info(f"发现 {len(files)} 个文件")
                
                for file in files:
                    if file.endswith('.json'):
                        article_path = os.path.join(module_dir, file)
                        current_app.logger.info(f"读取文章文件: {article_path}")
                        try:
                            with open(article_path, 'r', encoding='utf-8') as f:
                                article = json.load(f)
                                articles.append({
                                    'id': article.get('id', file.replace('.json', '')),
                                    'title': article.get('title', '无标题'),
                                    'created_at': article.get('created_at', ''),
                                    'updated_at': article.get('updated_at', ''),
                                    'created_by': article.get('created_by', ''),
                                    'updated_by': article.get('updated_by', '')
                                })
                                current_app.logger.info(f"成功加载文章: {article.get('title', '无标题')}")
                        except Exception as e:
                            current_app.logger.error(f"读取文章文件出错: {article_path}, 错误: {str(e)}")
            except Exception as e:
                current_app.logger.error(f"列出文章目录失败: {str(e)}")
        else:
            current_app.logger.warning(f"模块目录不存在: {module_dir}")
            # 确保模块目录存在
            os.makedirs(module_dir, exist_ok=True)
            current_app.logger.info(f"已创建模块目录: {module_dir}")
        
        # 将文章列表添加到模块数据中
        module['articles'] = articles
        current_app.logger.info(f"模块 {module_id} 包含 {len(articles)} 篇文章")
            
        current_app.logger.info(f"成功获取模块信息: {module_id}")
        return jsonify({'module': module, 'success': True})
    except Exception as e:
        current_app.logger.error(f"获取模块信息时出错: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@knowledge.route('/api/knowledge/module/<module_id>', methods=['PUT'])
@login_required
@admin_required
def update_module(module_id):
    """更新模块信息（仅管理员可用）"""
    try:
        current_app.logger.info(f"正在更新模块: {module_id}")
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            current_app.logger.error("更新模块时缺少name参数")
            return jsonify({'success': False, 'error': '缺少必要参数name'}), 400
            
        modules_file = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'modules.json')
        if not os.path.exists(modules_file):
            current_app.logger.error(f"模块配置文件不存在: {modules_file}")
            return jsonify({'success': False, 'error': '模块配置文件不存在'}), 404
            
        # 读取模块配置
        with open(modules_file, 'r', encoding='utf-8') as f:
            modules_data = json.load(f)
        
        current_app.logger.info(f"模块配置类型: {type(modules_data)}")
        
        # 兼容不同格式的模块配置
        if isinstance(modules_data, dict) and 'modules' in modules_data:
            modules_list = modules_data['modules']
        elif isinstance(modules_data, list):
            modules_list = modules_data
        else:
            current_app.logger.error(f"模块配置格式不支持: {type(modules_data)}")
            return jsonify({'success': False, 'error': '模块配置文件格式不支持'}), 500
            
        # 递归查找并更新模块
        def update_module_info(modules_list, target_id):
            for module in modules_list:
                if module.get('id') == target_id:
                    module['name'] = name
                    current_app.logger.info(f"找到并更新模块: {target_id} -> {name}")
                    return True
                if 'children' in module and isinstance(module['children'], list):
                    if update_module_info(module['children'], target_id):
                        return True
            return False
            
        # 执行更新
        if not update_module_info(modules_list, module_id):
            current_app.logger.error(f"未找到模块: {module_id}")
            return jsonify({'success': False, 'error': '模块不存在'}), 404
            
        # 保存更新后的模块配置
        with open(modules_file, 'w', encoding='utf-8') as f:
            if isinstance(modules_data, dict):
                modules_data['modules'] = modules_list
                json.dump(modules_data, f, ensure_ascii=False, indent=4)
            else:
                json.dump(modules_list, f, ensure_ascii=False, indent=4)
                
        current_app.logger.info(f"模块更新成功: {module_id}")
        return jsonify({'success': True, 'message': '模块更新成功'})
    except Exception as e:
        current_app.logger.error(f"更新模块时出错: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@knowledge.route('/api/knowledge/upload', methods=['POST'])
@login_required
@admin_required
def upload_article():
    """上传知识文档（仅管理员可用）"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
            
        file = request.files['file']
        title = request.form.get('title')
        module = request.form.get('module')
        
        if not file or not title or not module:
            return jsonify({'error': '缺少必要参数'}), 400
            
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
            
        # 生成文章ID
        article_id = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # 创建文章目录
        article_dir = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'articles', module, article_id)
        os.makedirs(article_dir, exist_ok=True)
        
        # 保存文件
        filename = secure_filename(file.filename)
        file_path = os.path.join(article_dir, filename)
        file.save(file_path)
        
        # 读取文件内容
        content = ''
        if filename.lower().endswith(('.txt', '.md')):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = f'<pre>{content}</pre>'
            except UnicodeDecodeError:
                content = f'<p>文件编码不支持，请下载查看：<a href="/api/knowledge/article/{article_id}/attachment/{filename}">{filename}</a></p>'
        else:
            content = f'<p>请下载附件查看：<a href="/api/knowledge/article/{article_id}/attachment/{filename}">{filename}</a></p>'
        
        # 保存文章信息
        article_data = {
            'id': article_id,
            'title': title,
            'module': module,
            'content': content,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'author': current_user.username,
            'attachment': filename
        }
        
        article_file = os.path.join(
            current_app.config['KNOWLEDGE_BASE_PATH'], 
            'articles', 
            module, 
            f'{article_id}.json'
        )
        
        with open(article_file, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=4)
            
        return jsonify({
            'success': True, 
            'article_id': article_id,
            'message': '文档上传成功',
            'path': os.path.join('articles', module, article_id)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/article', methods=['POST'])
@login_required
def create_article():
    """创建新文章"""
    try:
        # 尝试获取JSON数据
        try:
            data = request.get_json()
            if not data:
                data = request.form.to_dict()
        except Exception as e:
            current_app.logger.error(f"解析请求数据失败: {str(e)}")
            data = request.form.to_dict()
            
        current_app.logger.info(f"创建文章请求数据: {data}")
            
        title = data.get('title')
        module_id = data.get('module_id')
        content = data.get('content', '')
        
        current_app.logger.info(f"创建文章请求: 标题={title}, 模块ID={module_id}")
        
        if not title:
            current_app.logger.error("创建文章失败: 标题为空")
            return jsonify({'success': False, 'message': '文章标题不能为空'}), 400
            
        if not module_id:
            current_app.logger.error("创建文章失败: 模块ID为空")
            return jsonify({'success': False, 'message': '必须选择文章所属模块'}), 400
            
        # 确保知识库目录存在
        kb_path = current_app.config.get('KNOWLEDGE_BASE_PATH')
        if not kb_path:
            kb_path = os.path.join(current_app.root_path, 'data', 'knowledge_base')
            current_app.config['KNOWLEDGE_BASE_PATH'] = kb_path
            
        os.makedirs(kb_path, exist_ok=True)
        
        # 确保articles目录存在
        articles_path = os.path.join(kb_path, 'articles')
        os.makedirs(articles_path, exist_ok=True)
        
        # 确保模块目录存在
        module_dir = os.path.join(articles_path, module_id)
        if not os.path.exists(module_dir):
            current_app.logger.info(f"模块目录不存在，创建新目录: {module_dir}")
            os.makedirs(module_dir, exist_ok=True)
            
        # 生成文章ID
        article_id = f"article_{int(datetime.now().timestamp())}"
        current_app.logger.info(f"生成文章ID: {article_id}")
        
        # 创建文章JSON文件
        article_data = {
            'id': article_id,
            'title': title,
            'module_id': module_id,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'created_by': current_user.username,
            'updated_by': current_user.username
        }
        
        article_file = os.path.join(module_dir, f"{article_id}.json")
        current_app.logger.info(f"保存文章到文件: {article_file}")
        
        try:
            with open(article_file, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            
            # 添加短暂延迟，确保文件写入完成
            import time
            time.sleep(0.2)  # 等待200毫秒，让文件系统完成写入
            current_app.logger.info(f"文章数据已写入磁盘，并等待200ms确保写入完成")
        except Exception as e:
            current_app.logger.error(f"保存文章文件失败: {str(e)}")
            return jsonify({'success': False, 'message': f'文件保存失败: {str(e)}'}), 500
            
        # 更新模块配置，添加文章引用
        try:
            config_path = os.path.join(kb_path, 'modules.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    modules = json.load(f)
                
                # 确保modules是列表类型
                if not isinstance(modules, list):
                    current_app.logger.warning(f'模块数据格式不正确，可能影响文章列表显示')
                else:
                    # 清理已删除的文章引用
                    def clean_deleted_articles(modules_list):
                        for module in modules_list:
                            if 'articles' in module and isinstance(module['articles'], list):
                                # 检查每篇文章是否存在
                                articles_to_keep = []
                                for article in module['articles']:
                                    if not isinstance(article, dict) or 'id' not in article:
                                        continue
                                    
                                    # 检查文章文件是否存在
                                    article_exists = False
                                    for m_dir in os.listdir(articles_path):
                                        article_file_path = os.path.join(articles_path, m_dir, f"{article['id']}.json")
                                        if os.path.exists(article_file_path):
                                            article_exists = True
                                            break
                                    
                                    if article_exists:
                                        articles_to_keep.append(article)
                                    else:
                                        current_app.logger.info(f"清理不存在的文章引用: {article['id']}")
                                
                                module['articles'] = articles_to_keep
                            
                            # 递归处理子模块
                            if 'children' in module and isinstance(module['children'], list):
                                clean_deleted_articles(module['children'])
                    
                    # 清理已删除的文章引用
                    clean_deleted_articles(modules)
                    
                    # 递归查找模块并添加文章引用
                    def add_article_to_module(modules_list, target_module_id):
                        for module in modules_list:
                            if module['id'] == target_module_id:
                                if 'articles' not in module:
                                    module['articles'] = []
                                
                                # 添加文章引用
                                article_ref = {
                                    'id': article_id,
                                    'title': title
                                }
                                module['articles'].append(article_ref)
                                return True
                            
                            if 'children' in module and module['children']:
                                if add_article_to_module(module['children'], target_module_id):
                                    return True
                        return False
                    
                    # 更新模块中的文章引用
                    if add_article_to_module(modules, module_id):
                        # 保存更新后的模块配置
                        with open(config_path, 'w', encoding='utf-8') as f:
                            json.dump(modules, f, ensure_ascii=False, indent=2)
                        current_app.logger.info(f"文章引用已添加到模块: {module_id}")
                    else:
                        current_app.logger.warning(f'未找到对应模块，文章创建成功但未加入模块列表: {module_id}')
        except Exception as e:
            current_app.logger.error(f"更新模块配置失败，但文章已创建: {str(e)}")
            
        current_app.logger.info(f"文章创建成功: {title}, ID: {article_id}, 模块: {module_id}")
        return jsonify({
            'success': True,
            'message': '文章创建成功',
            'article_id': article_id,
            'module_id': module_id
        })
    except Exception as e:
        current_app.logger.error(f"创建文章失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'创建文章失败: {str(e)}'}), 500

@knowledge.route('/api/knowledge/upload-image', methods=['POST'])
@login_required
@admin_required
def upload_image():
    """上传图片（仅管理员可用）"""
    try:
        logging.info("正在处理图片上传请求")
        if 'image' not in request.files:
            logging.error("未找到上传的图片文件")
            return jsonify({'error': '没有上传图片'}), 400
            
        image = request.files['image']
        if image.filename == '':
            logging.error("图片文件名为空")
            return jsonify({'error': '未选择图片'}), 400
            
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in image.filename and 
                image.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            logging.error(f"不支持的图片格式: {image.filename}")
            return jsonify({'error': '不支持的图片格式'}), 400
            
        # 生成安全的文件名
        filename = secure_filename(image.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        new_filename = f"{timestamp}_{filename}"
        
        # 保存图片
        images_dir = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        image_path = os.path.join(images_dir, new_filename)
        image.save(image_path)
        logging.info(f"图片已保存: {image_path}")
        
        # 返回图片URL
        image_url = f"/api/knowledge/images/{new_filename}"
        logging.info(f"图片上传成功: {image_url}")
        return jsonify({
            'success': True,
            'url': image_url,
            'message': '图片上传成功'
        })
    except Exception as e:
        logging.error(f"上传图片时出错: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/images/<filename>')
@login_required
def get_image(filename):
    """获取图片"""
    try:
        images_dir = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'images')
        return send_file(os.path.join(images_dir, filename))
    except Exception as e:
        logging.error(f"获取图片时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/create-module', methods=['POST'])
def create_module():
    try:
        # 处理表单或JSON数据
        if request.is_json:
            data = request.get_json()
            name = data.get('name')
            parent_id = data.get('parent_id')
            description = data.get('description', '')
        else:
            name = request.form.get('name')
            parent_id = request.form.get('parent_id')
            description = request.form.get('description', '')
        
        current_app.logger.info(f'创建模块请求: 名称={name}, 父ID={parent_id}, 描述={description}')
        
        if not name:
            current_app.logger.warning('模块创建失败: 名称为空')
            return jsonify({'success': False, 'error': '模块名称不能为空'}), 400
        
        # 确保知识库目录存在
        kb_path = current_app.config.get('KNOWLEDGE_BASE_PATH')
        if not kb_path:
            kb_path = os.path.join(current_app.root_path, 'data', 'knowledge_base')
            current_app.config['KNOWLEDGE_BASE_PATH'] = kb_path
            
        os.makedirs(kb_path, exist_ok=True)
        
        # 确保articles目录存在
        articles_path = os.path.join(kb_path, 'articles')
        os.makedirs(articles_path, exist_ok=True)
        
        # 获取模块配置文件路径
        config_path = os.path.join(kb_path, 'modules.json')
        current_app.logger.info(f'模块配置文件路径: {config_path}')
        
        # 读取现有模块
        modules = []
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    modules = json.load(f)
                current_app.logger.info(f'已加载现有模块: {len(modules)}个')
            except Exception as e:
                current_app.logger.error(f'读取模块配置失败: {str(e)}')
                modules = []
        else:
            current_app.logger.info('模块配置文件不存在，将创建新文件')
        
        # 生成新模块ID
        module_id = f"module_{int(datetime.now().timestamp())}"
        
        # 创建新模块
        new_module = {
            'id': module_id,
            'name': name,
            'description': description,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'count': 0
        }
        
        # 如果指定了父模块，将新模块添加到父模块的children中
        if parent_id:
            def add_to_parent(modules_list, parent_id, new_module):
                for module in modules_list:
                    if module['id'] == parent_id:
                        if 'children' not in module:
                            module['children'] = []
                        module['children'].append(new_module)
                        current_app.logger.info(f'已将新模块添加到父模块: {parent_id}')
                        return True
                    if 'children' in module and module['children']:
                        if add_to_parent(module['children'], parent_id, new_module):
                            return True
                return False
            
            if not add_to_parent(modules, parent_id, new_module):
                current_app.logger.warning(f'父模块不存在: {parent_id}')
                return jsonify({'success': False, 'error': '父模块不存在'}), 400
        else:
            # 添加为顶级模块
            modules.append(new_module)
            current_app.logger.info('已将新模块添加为顶级模块')
        
        try:
            # 保存模块配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(modules, f, ensure_ascii=False, indent=2)
            current_app.logger.info('模块配置已保存')
            
            # 创建模块目录
            module_path = os.path.join(articles_path, module_id)
            os.makedirs(module_path, exist_ok=True)
            current_app.logger.info(f'模块目录已创建: {module_path}')
            
            return jsonify({
                'success': True,
                'module': new_module
            })
        except Exception as e:
            current_app.logger.error(f'保存模块配置失败: {str(e)}')
            return jsonify({'success': False, 'error': f'保存模块失败: {str(e)}'}), 500
            
    except Exception as e:
        current_app.logger.error(f'创建模块失败: {str(e)}')
        return jsonify({'success': False, 'error': f'创建模块失败: {str(e)}'}), 500

@knowledge.route('/api/knowledge/save-module', methods=['POST', 'HEAD', 'GET'])
@login_required
@admin_required
def save_module():
    """创建新模块（仅管理员可用）"""
    try:
        # 如果是HEAD或GET请求，仅用于API检测，直接返回成功
        if request.method in ['HEAD', 'GET']:
            return '', 200
        data = request.get_json()
        name = data.get('name')
        parent_id = data.get('parent_id')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'error': '模块名称不能为空'}), 400
            
        # 读取现有模块配置
        modules_file = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'modules.json')
        if os.path.exists(modules_file):
            with open(modules_file, 'r', encoding='utf-8') as f:
                modules_data = json.load(f)
        else:
            modules_data = {'modules': []}
            
        # 检查模块名称是否已存在
        def check_module_name(modules, name):
            for module in modules:
                if module.get('name') == name:
                    return True
                if 'children' in module and module['children']:
                    if check_module_name(module['children'], name):
                        return True
            return False
            
        if check_module_name(modules_data['modules'], name):
            return jsonify({'error': '模块名称已存在'}), 400
            
        # 生成唯一的模块ID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        module_id = f"m_{timestamp}_{secure_filename(name.lower())}"
        
        # 创建新模块
        new_module = {
            'id': module_id,
            'name': name,
            'description': description,
            'icon': 'fa-folder',
            'count': 0,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if parent_id:
            def add_to_parent(modules, parent_id, new_module):
                for module in modules:
                    if module['id'] == parent_id:
                        if 'children' not in module:
                            module['children'] = []
                        module['children'].append(new_module)
                        return True
                    if 'children' in module:
                        if add_to_parent(module['children'], parent_id, new_module):
                            return True
                return False
                
            if not add_to_parent(modules_data['modules'], parent_id, new_module):
                return jsonify({'error': '父模块不存在'}), 400
        else:
            modules_data['modules'].append(new_module)
            
        # 创建模块目录
        module_dir = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'articles', module_id)
        os.makedirs(module_dir, exist_ok=True)
        
        # 保存更新后的模块配置
        with open(modules_file, 'w', encoding='utf-8') as f:
            json.dump(modules_data, f, ensure_ascii=False, indent=4)
            
        return jsonify({
            'success': True,
            'module': new_module,
            'message': '模块创建成功'
        })
    except Exception as e:
        logging.error(f"创建模块时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_module_id(module):
    # 使用模块名称生成稳定的 ID
    if 'name' in module and module['name']:
        return 'mod_' + hashlib.md5(module['name'].encode('utf-8')).hexdigest()[:8]
    return module.get('id', '')

def update_module_ids(modules_list):
    for module in modules_list:
        # 如果模块 ID 为空或为临时 ID 格式（例如以'm_'开头但不是'mod_'），则重新生成
        if (not module.get('id')) or (module.get('id').startswith('m_') and not module.get('id').startswith('mod_')):
            module['id'] = generate_module_id(module)
        if 'children' in module and module['children']:
            update_module_ids(module['children'])

@knowledge.route('/api/knowledge/move-module', methods=['POST', 'HEAD'])
@login_required
@admin_required
def move_module():
    """移动模块（调整排序，仅管理员可用）"""
    # 处理 HEAD 请求
    if request.method == 'HEAD':
        return '', 200
        
    try:
        data = request.get_json()
        module_id = data.get('module_id')
        target_id = data.get('target_id')
        direction = data.get('direction', 'after')  # 默认移动到目标模块后面
        
        if not module_id:
            return jsonify({'error': '缺少必要参数 module_id'}), 400
            
        modules_file = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'modules.json')
        if not os.path.exists(modules_file):
            return jsonify({'error': '模块配置文件不存在'}), 404
            
        with open(modules_file, 'r', encoding='utf-8') as f:
            modules_data = json.load(f)
            
        # 更新所有模块的 ID
        if 'modules' in modules_data:
            update_module_ids(modules_data['modules'])
        
        # 查找模块和目标模块的位置
        def find_module_parent(modules_list, target_id, parent=None):
            for i, module in enumerate(modules_list):
                if module.get('id') == target_id:
                    return parent or modules_list, i
                if 'children' in module and module['children']:
                    result = find_module_parent(module['children'], target_id, module['children'])
                    if result[0] is not None:
                        return result
            return None, -1
        
        # 如果 target_id 为 null，则根据 direction 移动到顶部或底部
        if target_id is None:
            # 查找要移动的模块
            source_parent, source_index = find_module_parent(modules_data['modules'], module_id)
            
            if source_parent is None or source_index == -1:
                return jsonify({'error': '找不到要移动的模块'}), 404
                
            # 保存要移动的模块
            moving_module = source_parent[source_index]
            
            # 从原位置删除
            del source_parent[source_index]
            
            # 根据 direction 移动到顶部或底部
            if direction == 'up' or direction == 'before':
                # 移动到顶部
                modules_data['modules'].insert(0, moving_module)
            else:
                # 移动到底部
                modules_data['modules'].append(moving_module)
                
            # 保存更新后的模块配置
            with open(modules_file, 'w', encoding='utf-8') as f:
                json.dump(modules_data, f, ensure_ascii=False, indent=4)
                
            return jsonify({'success': True, 'message': '模块移动成功'})
            
        # 查找要移动的模块
        source_parent, source_index = find_module_parent(modules_data['modules'], module_id)
        target_parent, target_index = find_module_parent(modules_data['modules'], target_id)
        
        if source_parent is None or source_index == -1:
            return jsonify({'error': '找不到要移动的模块'}), 404
            
        if target_parent is None or target_index == -1:
            return jsonify({'error': '找不到目标模块'}), 404
            
        # 保存要移动的模块
        moving_module = source_parent[source_index]
        
        # 从原位置删除
        del source_parent[source_index]
        
        # 确定新位置
        new_index = target_index if direction == 'before' else target_index + 1
        
        # 插入到新位置
        target_parent.insert(new_index, moving_module)
        
        # 保存更新后的模块配置
        with open(modules_file, 'w', encoding='utf-8') as f:
            json.dump(modules_data, f, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True, 'message': '模块移动成功'})
    except Exception as e:
        logging.error(f"移动模块时出错: {str(e)}")
        return jsonify({'error': f'移动模块时出错: {str(e)}'}), 500

@knowledge.route('/api/knowledge/delete-module', methods=['POST', 'HEAD'])
@login_required
@admin_required
def delete_module_post():
    """删除模块（仅管理员可用）- POST方法"""
    try:
        # 如果是HEAD请求，直接返回成功
        if request.method == 'HEAD':
            return '', 200
            
        data = request.get_json()
        module_id = data.get('module_id')
        
        if not module_id:
            return jsonify({'error': '模块ID不能为空'}), 400
            
        modules_file = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'modules.json')
        if not os.path.exists(modules_file):
            return jsonify({'error': '模块配置文件不存在'}), 404
            
        with open(modules_file, 'r', encoding='utf-8') as f:
            modules = json.load(f)
            
        # 删除模块（递归删除子模块）
        def remove_module(modules_list, target_id):
            for i, module in enumerate(modules_list):
                if module['id'] == target_id:
                    # 删除模块目录及其内容
                    module_dir = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'articles', target_id)
                    if os.path.exists(module_dir):
                        for root, dirs, files in os.walk(module_dir, topdown=False):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))
                        os.rmdir(module_dir)
                    
                    # 递归删除子模块
                    if 'children' in module and module['children']:
                        for child in module['children']:
                            remove_module(module['children'], child['id'])
                    
                    del modules_list[i]
                    return True
                elif 'children' in module and module['children']:
                    if remove_module(module['children'], target_id):
                        return True
            return False
            
        if not remove_module(modules['modules'], module_id):
            return jsonify({'error': '模块不存在'}), 404
            
        # 保存更新后的模块配置
        with open(modules_file, 'w', encoding='utf-8') as f:
            json.dump(modules, f, ensure_ascii=False, indent=4)
            
        return jsonify({'success': True, 'message': '模块删除成功'})
    except Exception as e:
        logging.error(f"删除模块时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/check-api', methods=['GET'])
def check_api():
    """检查API是否可用"""
    try:
        endpoint = request.args.get('endpoint')
        if not endpoint:
            return jsonify({'error': '缺少endpoint参数'}), 400
            
        # 可用的API端点列表
        available_apis = {
            'save-module': True,
            'delete-module': True,
            'move-module': True,
            'upload-image': True,
            'save-article': True,  # 添加文章保存API检查
            'create-article': True # 添加文章创建API检查
        }
        
        if endpoint in available_apis:
            return jsonify({
                'available': available_apis[endpoint],
                'endpoint': endpoint,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return jsonify({
                'available': False,
                'endpoint': endpoint,
                'error': '未知的API端点',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    except Exception as e:
        current_app.logger.error(f"检查API时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@knowledge.route('/reports/<report_id>', methods=['GET'])
def view_report(report_id):
    """查看报告"""
    try:
        # 使用项目根目录的 reports 文件夹
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'reports')
        
        # 确保report_id包含.html后缀
        if not report_id.endswith('.html'):
            report_id = report_id + '.html'
            
        report_path = os.path.join(reports_dir, report_id)
        
        current_app.logger.info(f'尝试读取报告: {report_path}')
        
        if not os.path.exists(report_path):
            current_app.logger.error(f'报告不存在: {report_path}')
            return '报告不存在', 404
            
        # 使用send_from_directory发送文件
        return send_from_directory(reports_dir, report_id)
    except Exception as e:
        current_app.logger.error(f'读取报告失败: {str(e)}')
        return '读取报告失败', 500

@knowledge.route('/reports/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    """删除报告"""
    try:
        # 使用相对路径 'reports'
        reports_dir = 'reports'
        report_path = os.path.join(reports_dir, report_id)
        
        current_app.logger.info(f'尝试删除报告: {report_path}')
        
        if os.path.exists(report_path):
            os.remove(report_path)
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '报告不存在'})
    except Exception as e:
        current_app.logger.error(f'删除报告失败: {str(e)}')
        return jsonify({'success': False, 'message': str(e)})

@knowledge.route('/nas_finder')
@login_required
def nas_finder():
    """NAS设备查询页面"""
    # 从 JSON 文件加载问题和答案
    questions_file = os.path.join(current_app.root_path, 'nas_devices', 'questions.json')
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

@knowledge.route('/api/knowledge/nas_devices', methods=['GET', 'POST'])
@login_required
def nas_devices():
    """NAS设备信息 API"""
    try:
        if request.method == 'POST':
            # 严格检查管理员权限
            if not current_user.is_admin():
                return jsonify({'error': '权限不足，只有管理员可以添加设备'}), 403
                
            data = request.get_json()
            devices_data = load_nas_devices()
            
            # 生成设备ID
            device_id = f"device_{int(datetime.now().timestamp())}"
            
            # 创建新设备
            new_device = {
                'id': device_id,
                'brand': data.get('brand'),
                'model': data.get('model'),
                'ip': data.get('ip'),
                'username': data.get('username'),
                'password': data.get('password')
            }
            
            # 添加到对应类型的列表中
            device_type = data.get('type', 'storage')
            if device_type not in devices_data:
                devices_data[device_type] = []
            devices_data[device_type].append(new_device)
            
            # 保存设备信息
            save_nas_devices(devices_data)
            
            return jsonify({'success': True, 'device': new_device, 'type': device_type})
        else:
            # 获取设备列表 - 非管理员需要通过验证才能查看
            if not current_user.is_admin():
                # 检查是否已通过验证
                device_type = request.args.get('type', 'storage')
                session_key = f"{device_type}_authenticated"
                if flask_session.get(session_key) != True:
                    return jsonify({'devices': [], 'error': '需要验证才能查看设备列表'}), 403
            
            # 获取设备列表
            device_type = request.args.get('type', 'storage')
            devices_data = load_nas_devices()
            return jsonify({'devices': devices_data.get(device_type, [])})
            
    except Exception as e:
        current_app.logger.error(f'处理NAS设备信息时出错: {str(e)}')
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/nas_devices/<device_id>', methods=['DELETE'])
@login_required
def delete_nas_device(device_id):
    """删除NAS设备"""
    try:
        # 严格检查管理员权限
        if not current_user.is_admin():
            return jsonify({'error': '权限不足，只有管理员可以删除设备'}), 403
            
        devices_data = load_nas_devices()
        
        # 在所有类型中查找并删除设备
        for device_type in devices_data:
            devices = devices_data[device_type]
            for i, device in enumerate(devices):
                if device.get('id') == device_id:
                    del devices[i]
                    save_nas_devices(devices_data)
                    return jsonify({'success': True})
                    
        return jsonify({'error': '设备不存在'}), 404
    except Exception as e:
        current_app.logger.error(f'删除NAS设备时出错: {str(e)}')
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/nas_devices/delete', methods=['POST'])
@login_required
def delete_nas_device_post():
    """通过POST方法删除NAS设备"""
    try:
        # 严格检查管理员权限
        if not current_user.is_admin():
            return jsonify({'error': '权限不足，只有管理员可以删除设备'}), 403
            
        data = request.get_json()
        device_id = data.get('id')
        device_type = data.get('type')
        
        if not device_id:
            return jsonify({'error': '设备ID不能为空'}), 400
            
        devices_data = load_nas_devices()
        
        # 如果提供了设备类型，只在该类型中查找
        if device_type and device_type in devices_data:
            devices = devices_data[device_type]
            for i, device in enumerate(devices):
                if device.get('id') == device_id:
                    del devices[i]
                    save_nas_devices(devices_data)
                    return jsonify({'success': True})
        else:
            # 在所有类型中查找并删除设备
            for type_key in devices_data:
                devices = devices_data[type_key]
                for i, device in enumerate(devices):
                    if device.get('id') == device_id:
                        del devices[i]
                        save_nas_devices(devices_data)
                        return jsonify({'success': True})
                    
        return jsonify({'error': '设备不存在'}), 404
    except Exception as e:
        current_app.logger.error(f'删除NAS设备时出错: {str(e)}')
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/nas_devices/update', methods=['POST'])
@login_required
def update_nas_device():
    """更新NAS设备信息"""
    try:
        # 严格检查管理员权限
        if not current_user.is_admin():
            return jsonify({'error': '权限不足，只有管理员可以更新设备信息'}), 403
            
        data = request.get_json()
        device_id = data.get('id')
        device_type = data.get('type')
        
        if not device_id:
            return jsonify({'error': '设备ID不能为空'}), 400
            
        devices_data = load_nas_devices()
        
        # 更新设备信息
        device_found = False
        
        # 如果提供了设备类型，只在该类型中查找
        if device_type and device_type in devices_data:
            devices = devices_data[device_type]
            for i, device in enumerate(devices):
                if device.get('id') == device_id:
                    # 更新设备信息
                    devices[i] = {
                        'id': device_id,
                        'brand': data.get('brand', device.get('brand')),
                        'model': data.get('model', device.get('model')),
                        'ip': data.get('ip', device.get('ip')),
                        'username': data.get('username', device.get('username')),
                        'password': data.get('password', device.get('password'))
                    }
                    device_found = True
                    break
        else:
            # 在所有类型中查找设备
            for type_key in devices_data:
                devices = devices_data[type_key]
                for i, device in enumerate(devices):
                    if device.get('id') == device_id:
                        # 更新设备信息
                        devices[i] = {
                            'id': device_id,
                            'brand': data.get('brand', device.get('brand')),
                            'model': data.get('model', device.get('model')),
                            'ip': data.get('ip', device.get('ip')),
                            'username': data.get('username', device.get('username')),
                            'password': data.get('password', device.get('password'))
                        }
                        device_found = True
                        break
                if device_found:
                    break
        
        if device_found:
            save_nas_devices(devices_data)
            return jsonify({'success': True, 'type': device_type})
        else:
            return jsonify({'error': '设备不存在'}), 404
    except Exception as e:
        current_app.logger.error(f'更新NAS设备时出错: {str(e)}')
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/nas_question', methods=['GET', 'POST'])
@login_required
def nas_question():
    """NAS设备访问问题"""
    try:
        questions_file = os.path.join(current_app.root_path, 'nas_devices', 'questions.json')
        
        if request.method == 'POST':
            # 严格检查管理员权限
            if not current_user.is_admin():
                return jsonify({'error': '权限不足，只有管理员可以设置问题'}), 403
                
            data = request.get_json()
            
            # 确保接收到的数据格式正确
            if not isinstance(data, dict) or 'storage' not in data or 'performance' not in data:
                return jsonify({'error': '数据格式不正确'}), 400
                
            # 确保每个组都包含name、question和answer字段
            if ('name' not in data['storage'] or 'question' not in data['storage'] or 'answer' not in data['storage'] or
                'name' not in data['performance'] or 'question' not in data['performance'] or 'answer' not in data['performance']):
                return jsonify({'error': '请提供完整的组名、问题和答案'}), 400
            
            # 确保目录存在
            os.makedirs(os.path.dirname(questions_file), exist_ok=True)
            
            # 保存问题
            with open(questions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            return jsonify({'success': True})
        else:
            # 获取问题
            if os.path.exists(questions_file):
                with open(questions_file, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                return jsonify(questions)
            else:
                # 返回默认设置
                return jsonify({
                    'storage': {
                        'name': '存储组',
                        'question': '请输入存储组访问密码:',
                        'answer': 'admin'
                    },
                    'performance': {
                        'name': '性能专项组',
                        'question': '请输入性能专项组访问密码:',
                        'answer': 'admin'
                    }
                })
    except Exception as e:
        current_app.logger.error(f'处理NAS设备访问问题时出错: {str(e)}')
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/nas_auth', methods=['POST'])
@login_required
def nas_auth():
    """验证用户回答的问题以访问NAS设备列表"""
    try:
        # 管理员直接通过验证
        if current_user.is_admin():
            current_app.logger.info(f"管理员用户 {current_user.username} 自动通过验证")
            return jsonify({'authenticated': True})
            
        data = request.json if request.json else request.get_json()
        if not data:
            current_app.logger.error("请求数据为空")
            return jsonify({'authenticated': False, 'error': '请求数据为空'}), 400
            
        device_type = data.get('type')  # 使用'type'作为参数名
        answer = data.get('answer')
        
        current_app.logger.info(f"用户 {current_user.username} 尝试验证 {device_type} 设备访问，提交答案: {answer}")
        
        if not device_type or not answer:
            current_app.logger.error(f"缺少必要参数: device_type={device_type}, answer={answer}")
            return jsonify({'authenticated': False, 'error': '参数不完整'}), 400
            
        # 加载问题
        questions_file = os.path.join(current_app.root_path, 'nas_devices', 'questions.json')
        if os.path.exists(questions_file):
            try:
                with open(questions_file, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                current_app.logger.info(f"成功加载问题文件: {questions_file}")
            except Exception as e:
                current_app.logger.error(f'读取问题文件失败: {str(e)}')
                questions = {
                    'storage': {'question': '默认存储组问题', 'answer': 'admin'},
                    'performance': {'question': '默认性能组问题', 'answer': 'admin'}
                }
        else:
            current_app.logger.warning('问题文件不存在，使用默认问题')
            questions = {
                'storage': {'question': '默认存储组问题', 'answer': 'admin'},
                'performance': {'question': '默认性能组问题', 'answer': 'admin'}
            }
            
        # 验证答案
        device_info = questions.get(device_type, {})
        correct_answer = device_info.get('answer', '')
        
        current_app.logger.info(f"问题类型: {device_type}, 正确答案: {correct_answer}, 用户答案: {answer}")
        
        # 确保两者都是字符串类型并且去除首尾空格再比较
        if isinstance(answer, str) and isinstance(correct_answer, str) and answer.strip() == correct_answer.strip():
            # 保存验证状态到会话
            flask_session[f"{device_type}_authenticated"] = True
            current_app.logger.info(f"用户 {current_user.username} 验证成功，设置会话状态: {device_type}_authenticated=True")
            return jsonify({'authenticated': True})
        else:
            current_app.logger.warning(f"用户 {current_user.username} 验证失败，答案不匹配")
            return jsonify({'authenticated': False, 'message': '答案错误，请重试'})
    except Exception as e:
        current_app.logger.error(f'验证NAS设备访问权限时出错: {str(e)}', exc_info=True)
        return jsonify({'authenticated': False, 'error': f'服务器内部错误: {str(e)}'}), 500

def load_nas_devices():
    """加载NAS设备信息"""
    devices_file = os.path.join(current_app.root_path, 'nas_devices', 'devices.json')
    if not os.path.exists(devices_file):
        return {'storage': [], 'performance': []}
        
    try:
        with open(devices_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        current_app.logger.error(f'加载NAS设备信息失败: {str(e)}')
        return {'storage': [], 'performance': []}

def save_nas_devices(devices_data):
    """保存NAS设备信息"""
    devices_file = os.path.join(current_app.root_path, 'nas_devices', 'devices.json')
    os.makedirs(os.path.dirname(devices_file), exist_ok=True)
    
    try:
        with open(devices_file, 'w', encoding='utf-8') as f:
            json.dump(devices_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        current_app.logger.error(f'保存NAS设备信息失败: {str(e)}')
        raise

@knowledge.route('/api/knowledge/batch_check', methods=['POST'])
@login_required
def batch_check_devices():
    """批量检查设备状态"""
    try:
        data = request.get_json()
        device_ids = data.get('device_ids', [])
        
        if not device_ids:
            return jsonify({'error': '未选择任何设备'}), 400
            
        devices_data = load_nas_devices()
        results = []
        
        for device_id in device_ids:
            device = None
            # 在所有设备组中查找设备
            for group in devices_data.values():
                for d in group:
                    if d.get('id') == device_id:
                        device = d
                        break
                if device:
                    break
                    
            if not device:
                results.append({
                    'id': device_id,
                    'status': 'error',
                    'message': '设备不存在'
                })
                continue
                
            try:
                # 尝试连接设备
                response = requests.get(
                    f"http://{device['ip']}:9999/system/check",
                    timeout=2
                )
                if response.status_code == 200:
                    results.append({
                        'id': device_id,
                        'status': 'success',
                        'message': '设备在线',
                        'data': response.json()
                    })
                else:
                    results.append({
                        'id': device_id,
                        'status': 'error',
                        'message': f'设备返回错误状态码: {response.status_code}'
                    })
            except requests.exceptions.RequestException as e:
                results.append({
                    'id': device_id,
                    'status': 'error',
                    'message': f'连接设备失败: {str(e)}'
                })
                
        return jsonify({'results': results})
    except Exception as e:
        current_app.logger.error(f'批量检查设备状态时出错: {str(e)}')
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/batch_update', methods=['POST'])
@login_required
@admin_required
def batch_update_devices():
    """批量更新设备配置"""
    try:
        data = request.get_json()
        device_ids = data.get('device_ids', [])
        config = data.get('config', {})
        
        if not device_ids:
            return jsonify({'error': '未选择任何设备'}), 400
            
        if not config:
            return jsonify({'error': '未提供配置信息'}), 400
            
        devices_data = load_nas_devices()
        results = []
        
        for device_id in device_ids:
            device = None
            device_type = None
            # 在所有设备组中查找设备
            for type_name, group in devices_data.items():
                for i, d in enumerate(group):
                    if d.get('id') == device_id:
                        device = d
                        device_type = type_name
                        # 更新设备配置
                        devices_data[type_name][i].update(config)
                        break
                if device:
                    break
                    
            if not device:
                results.append({
                    'id': device_id,
                    'status': 'error',
                    'message': '设备不存在'
                })
                continue
                
            results.append({
                'id': device_id,
                'status': 'success',
                'message': '配置已更新'
            })
            
        # 保存更新后的设备信息
        save_nas_devices(devices_data)
        return jsonify({'results': results})
    except Exception as e:
        current_app.logger.error(f'批量更新设备配置时出错: {str(e)}')
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/batch_monitor', methods=['POST'])
@login_required
def batch_monitor_devices():
    """批量监控设备状态"""
    try:
        data = request.get_json()
        device_ids = data.get('device_ids', [])
        
        if not device_ids:
            return jsonify({'error': '未选择任何设备'}), 400
            
        devices_data = load_nas_devices()
        results = []
        
        for device_id in device_ids:
            device = None
            # 在所有设备组中查找设备
            for group in devices_data.values():
                for d in group:
                    if d.get('id') == device_id:
                        device = d
                        break
                if device:
                    break
                    
            if not device:
                results.append({
                    'id': device_id,
                    'status': 'error',
                    'message': '设备不存在'
                })
                continue
                
            try:
                # 获取设备状态信息
                status_response = requests.get(
                    f"http://{device['ip']}:9999/system/status",
                    timeout=2
                )
                # 获取设备性能信息
                perf_response = requests.get(
                    f"http://{device['ip']}:9999/system/performance",
                    timeout=2
                )
                
                if status_response.status_code == 200 and perf_response.status_code == 200:
                    results.append({
                        'id': device_id,
                        'status': 'success',
                        'data': {
                            'system_status': status_response.json(),
                            'performance': perf_response.json()
                        }
                    })
                else:
                    results.append({
                        'id': device_id,
                        'status': 'error',
                        'message': '获取设备信息失败'
                    })
            except requests.exceptions.RequestException as e:
                results.append({
                    'id': device_id,
                    'status': 'error',
                    'message': f'连接设备失败: {str(e)}'
                })
                
        return jsonify({'results': results})
    except Exception as e:
        current_app.logger.error(f'批量监控设备状态时出错: {str(e)}')
        return jsonify({'error': str(e)}), 500

@knowledge.route('/api/knowledge/article/<article_id>', methods=['PUT'])
@login_required
def update_article(article_id):
    """更新文章内容"""
    try:
        current_app.logger.info(f"正在更新文章: {article_id}")
        data = request.get_json()
        if not data:
            current_app.logger.error("更新文章时请求数据为空")
            return jsonify({'success': False, 'error': '请求数据为空'}), 400
            
        content = data.get('content')
        title = data.get('title')
        
        # 如果既没有content也没有title，返回错误
        if not content and not title:
            current_app.logger.error("更新文章时缺少content或title参数")
            return jsonify({'success': False, 'error': '缺少必要参数content或title'}), 400
            
        # 遍历所有模块目录查找文章
        articles_dir = os.path.join(current_app.config['KNOWLEDGE_BASE_PATH'], 'articles')
        if not os.path.exists(articles_dir):
            os.makedirs(articles_dir, exist_ok=True)
            current_app.logger.warning(f"文章目录不存在，已创建: {articles_dir}")

        article_found = False
        
        current_app.logger.info(f"开始查找文章: {article_id}")
        for module in os.listdir(articles_dir):
            module_path = os.path.join(articles_dir, module)
            if not os.path.isdir(module_path):
                continue
                
            article_file = os.path.join(module_path, f'{article_id}.json')
            if os.path.exists(article_file):
                article_found = True
                current_app.logger.info(f"找到文章文件: {article_file}")
                
                try:
                    with open(article_file, 'r', encoding='utf-8') as f:
                        article = json.load(f)
                    
                    # 更新内容和标题（如果提供了）
                    if content is not None:
                        article['content'] = content
                        current_app.logger.info(f"准备更新内容，长度: {len(content)}")
                    
                    if title is not None:
                        article['title'] = title
                        current_app.logger.info(f"准备更新标题: {title}")
                    
                    article['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    article['updated_by'] = current_user.username
                    
                    with open(article_file, 'w', encoding='utf-8') as f:
                        json.dump(article, f, ensure_ascii=False, indent=4)
                        
                    current_app.logger.info(f"文章更新成功: {article_id}")
                    return jsonify({'success': True, 'message': '文章更新成功'})
                except Exception as e:
                    current_app.logger.error(f"更新文章出错: {str(e)}", exc_info=True)
                    return jsonify({'success': False, 'error': f'更新文章时发生错误: {str(e)}'}), 500
        
        if not article_found:
            current_app.logger.error(f"未找到文章: {article_id}")
            return jsonify({'success': False, 'error': '文章不存在'}), 404
            
    except Exception as e:
        current_app.logger.error(f"更新文章时出错: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500