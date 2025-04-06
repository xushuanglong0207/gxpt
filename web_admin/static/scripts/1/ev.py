#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import sys
from pathlib import Path  # 用于处理本地路径
from utils import UtilsDriver  # 确保 utils.py 在相同目录下
from colorama import init, Fore, Style

# 初始化 colorama
init(autoreset=True)

def main():
    # 打印当前工作目录
    print(f"当前工作目录: {Path.cwd()}")
    # 读取配置文件

    # 获取脚本所在目录的绝对路径
    script_dir = Path(__file__).parent.resolve()
    print(f"脚本所在目录: {script_dir}")  # 添加调试信息
    config = configparser.ConfigParser()
#    config.read('../config/config98.ini')
    config.read('../config/config214.ini')


    host = config['ssh']['host']
    username = config['ssh']['username']
    password = config['ssh']['password']
    #password = UtilsDriver.NAS_PASSWORD    # 使用UtilsDriver中定义的密码



    public_patch = "/test/dd"
    # 要创建的文件及其本地路径
    scripts = {
        # f"{public_patch}/dd.sh": script_dir / "dd.sh",
        # f"{public_patch}/autodd.sh": script_dir / "autodd.sh",
        f"{public_patch}/speedmonitor.py": script_dir / "speedmonitor.py"

    }

    try:
        # 连接到SSH服务器
        UtilsDriver.connect_ssh(host=host, username=username, password=password,port=22)
    except Exception as e:
        print(f"{Fore.RED}SSH连接失败: {e}{Style.RESET_ALL}")
        sys.exit(1)

    try:
        # 创建远程目录并设置权限
        mkdir_command = f"mkdir -p {public_patch} && chmod 777 {public_patch}"
        UtilsDriver.execute_command(mkdir_command)
        print(f"{Fore.GREEN}已创建或确认远程目录: /test/thumb{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}创建远程目录失败: {e}{Style.RESET_ALL}")
        UtilsDriver.close_ssh_connection()
        sys.exit(1)

    try:
        # 创建并写入文件
        for remote_path, local_path in scripts.items():
            print(f"准备创建并写入文件: {remote_path}")
            try:
                # 读取本地文件内容
                with open(local_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 使用 SSH 命令在远程服务器上创建文件并写入内容
                UtilsDriver.create_remote_file(remote_path, content)
                print(f"{Fore.GREEN}成功创建并写入文件: {remote_path}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}创建文件失败: {remote_path} | 错误: {e}{Style.RESET_ALL}")
                # 不立即退出，继续尝试创建下一个文件
    except Exception as e:
        print(f"{Fore.RED}创建文件过程中发生错误: {e}{Style.RESET_ALL}")
        UtilsDriver.close_ssh_connection()
        sys.exit(1)

    try:
        # 设置文件可执行权限
        chmod_command = f"chmod +x {public_patch}/*"
        UtilsDriver.execute_command(chmod_command)
        print(f"{Fore.GREEN}已设置脚本的可执行权限{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}设置可执行权限失败: {e}{Style.RESET_ALL}")
        UtilsDriver.close_ssh_connection()
        sys.exit(1)

    # try:
    #     # 执行安装脚本，确保使用正斜杠
    #     install_script = f"{public_patch}/cgroup-sort.sh"
    #     execute_install = f"bash {install_script}"
    #     UtilsDriver.execute_command(execute_install)
    #     print(f"{Fore.GREEN}已执行 cgroup-sort.sh 脚本{Style.RESET_ALL}")
    # except Exception as e:
    #     print(f"{Fore.RED}执行 cgroup-sort.sh 脚本失败: {e}{Style.RESET_ALL}")
    #     UtilsDriver.close_ssh_connection()
    #     sys.exit(1)

    try:
        # 安装Python模块的Debian包
        required_debian_packages = [
            'python3-psutil',
            'python3-colorama',
            'python3-tabulate',
            'python3-flask',
            'bc'
        ]
        install_python_packages = f"apt-get install -y {' '.join(required_debian_packages)}"
        UtilsDriver.execute_command(install_python_packages)
        print(f"{Fore.GREEN}已安装所需的Python模块包{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}安装Python模块包失败: {e}{Style.RESET_ALL}")
        UtilsDriver.close_ssh_connection()
        sys.exit(1)

    # 关闭SSH连接
    UtilsDriver.close_ssh_connection()
    print(f"{Fore.GREEN}部署完成。{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
