#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def check_package(package_name):
    """检查包是否已安装"""
    try:
        __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        return False

def install_package(package):
    """安装指定的包"""
    print(f"正在安装 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} 安装成功!")
        return True
    except subprocess.CalledProcessError:
        print(f"{package} 安装失败，请手动安装。")
        return False

def main():
    """主函数"""
    print("=== Web后台依赖安装工具 ===")
    
    # 检查必要的包
    required_packages = [
        "flask",
        "flask-login",
        "werkzeug",
        "jinja2",
    ]
    
    need_install = False
    for package in required_packages:
        if not check_package(package.replace('-', '_')):
            print(f"缺少依赖: {package}")
            need_install = True
    
    if need_install:
        print("\n开始安装缺少的依赖...")
        for package in required_packages:
            if not check_package(package.replace('-', '_')):
                install_package(package)
        
        print("\n所有依赖已安装完成。现在可以运行 Web 后台了:")
        print("python web_admin/app.py")
    else:
        print("\n所有依赖已安装。你可以直接运行 Web 后台:")
        print("python web_admin/app.py")

if __name__ == "__main__":
    main() 