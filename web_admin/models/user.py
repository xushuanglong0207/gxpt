#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import hashlib
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# 用户数据文件路径
USER_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.json')

# 确保数据目录存在
os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)

class User(UserMixin):
    """用户模型"""
    
    def __init__(self, id, username, password_hash, role='user', email=None, created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'admin' 或 'user'
        self.email = email
        self.created_at = created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @classmethod
    def get(cls, user_id):
        """Flask-Login 需要的方法，根据用户ID获取用户实例"""
        return cls.get_user_by_id(user_id)

    def get_id(self):
        """Flask-Login 需要的方法，返回用户ID的字符串表示"""
        return str(self.id)
    
    def is_admin(self):
        """检查用户是否为管理员"""
        return self.role == 'admin'
    
    def to_dict(self):
        """将用户对象转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'email': self.email,
            'created_at': self.created_at
        }
    
    @staticmethod
    def hash_password(password):
        """对密码进行哈希处理"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def check_password(password_hash, password):
        """检查密码是否正确"""
        return password_hash == User.hash_password(password)
    
    @staticmethod
    def get_all_users():
        """获取所有用户"""
        if not os.path.exists(USER_DATA_FILE):
            # 如果用户数据文件不存在，创建一个空文件
            try:
                with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                print(f"创建用户数据文件: {USER_DATA_FILE}")
            except Exception as e:
                print(f"创建用户数据文件失败: {str(e)}")
            return []
        
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                users = []
                for user_data in users_data:
                    try:
                        users.append(User(**user_data))
                    except Exception as e:
                        print(f"解析用户数据失败: {str(e)}, 数据: {user_data}")
                return users
        except json.JSONDecodeError as e:
            print(f"用户数据文件格式错误: {str(e)}")
            # 备份损坏的文件并创建新文件
            backup_file = f"{USER_DATA_FILE}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            try:
                os.rename(USER_DATA_FILE, backup_file)
                print(f"已备份损坏的用户数据文件: {backup_file}")
                with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                print(f"已创建新的用户数据文件")
            except Exception as e:
                print(f"备份/创建用户数据文件失败: {str(e)}")
            return []
        except Exception as e:
            print(f"读取用户数据失败: {str(e)}")
            return []
    
    @staticmethod
    def get_user_by_id(user_id):
        """根据ID获取用户"""
        users = User.get_all_users()
        for user in users:
            if user.id == user_id:
                return user
        return None
    
    @staticmethod
    def get_user_by_username(username):
        """根据用户名获取用户"""
        users = User.get_all_users()
        for user in users:
            if user.username == username:
                return user
        return None
    
    @staticmethod
    def create_user(username, password, role='user', email=None):
        """创建新用户"""
        # 检查用户名是否已存在
        if User.get_user_by_username(username):
            return False, "用户名已存在"
        
        # 获取所有用户
        users = User.get_all_users()
        
        # 生成新用户ID
        new_id = str(len(users) + 1)
        
        # 创建新用户
        new_user = User(
            id=new_id,
            username=username,
            password_hash=User.hash_password(password),
            role=role,
            email=email
        )
        
        # 添加到用户列表
        users.append(new_user)
        
        # 保存用户数据
        try:
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([user.to_dict() for user in users], f, ensure_ascii=False, indent=2)
            return True, new_user
        except Exception as e:
            print(f"保存用户数据失败: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """更新用户信息"""
        users = User.get_all_users()
        updated = False
        
        for i, user in enumerate(users):
            if user.id == user_id:
                # 更新用户信息
                for key, value in kwargs.items():
                    if key == 'password':
                        # 如果更新密码，需要进行哈希处理
                        setattr(user, 'password_hash', User.hash_password(value))
                    elif hasattr(user, key):
                        # 只更新对象存在的属性
                        setattr(user, key, value)
                updated = True
                break
        
        if not updated:
            return False, "用户不存在"
        
        # 保存用户数据
        try:
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([user.to_dict() for user in users], f, ensure_ascii=False, indent=2)
            return True, "用户更新成功"
        except Exception as e:
            print(f"保存用户数据失败: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        users = User.get_all_users()
        users = [user for user in users if user.id != user_id]
        
        # 保存用户数据
        try:
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([user.to_dict() for user in users], f, ensure_ascii=False, indent=2)
            return True, "用户删除成功"
        except Exception as e:
            print(f"保存用户数据失败: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def init_admin_user():
        """初始化管理员用户"""
        # 检查是否已有管理员用户
        users = User.get_all_users()
        admin_exists = any(user.role == 'admin' for user in users)
        
        if not admin_exists:
            # 创建默认管理员用户
            return User.create_user(
                username='admin',
                password='admin123',
                role='admin',
                email='admin@example.com'
            )
        
        return True, "管理员用户已存在" 