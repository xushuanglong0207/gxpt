#!/usr/bin/env python3
import subprocess
import time
import os
import shutil
import re
import statistics
from datetime import datetime
import psutil
import argparse
import socket
import base64
import sys

parser = argparse.ArgumentParser(description="DD磁盘写入测试")
parser.add_argument('output_dir', type=str, help="输出目录路径或块设备(如/dev/sda)")
parser.add_argument('run_time', type=int, help="运行时间（秒）")
parser.add_argument('--bs', type=str, default="1M", help="块大小，如：4k, 8k, 16k, 1M, 4M, 8M")
args = parser.parse_args()

# 获取当前测试设备名称
device_name = socket.gethostname()


# 检测系统类型和版本
def detect_system_info():
    system_type = "未知系统"
    system_version = "未知版本"
    write_destination = "未知"

    try:
        # 获取uname信息
        uname_output = subprocess.check_output(["uname", "-a"], text=True).strip()

        # 检测系统类型
        if "DH" in uname_output or "DXP" in uname_output:
            system_type = "ugos pro系统"
        elif "z" in uname_output and "DH" not in uname_output and "DXP" not in uname_output:
            system_type = "极空间系统"

        # 获取版本信息
        if os.path.exists("/etc/os-release"):
            os_release = subprocess.check_output(["cat", "/etc/os-release"], text=True).strip()

            if system_type == "ugos pro系统":
                match = re.search(r'OS_VERSION=([0-9\.]+)', os_release)
                if match:
                    system_version = match.group(1)
            elif system_type == "极空间系统":
                match = re.search(r'ZOS_VERSION="([^"]+)"', os_release)
                if match:
                    system_version = match.group(1)

        # 确定写入目的地
        if is_block_device(args.output_dir):
            # 如果是直接对块设备进行测试
            write_destination = args.output_dir
            if re.match(r'/dev/sd[a-z]$', args.output_dir):
                destination_type = "硬盘"
            elif re.match(r'/dev/sd[a-z][0-9]+', args.output_dir):
                destination_type = "硬盘分区"
            elif re.match(r'/dev/md[0-9]+', args.output_dir):
                destination_type = "raid块设备"
            else:
                destination_type = "块设备"
            write_destination = f"{destination_type}：{args.output_dir}"
        else:
            # 如果是对目录进行测试，检查底层设备
            try:
                df_output = subprocess.check_output(["df", "-h", args.output_dir], text=True).strip()

                # 检查是硬盘、分区、RAID还是文件系统
                if "/dev/sd" in df_output:
                    if re.search(r'/dev/sd[a-z]$', df_output):
                        write_destination = re.search(r'(/dev/sd[a-z])(?:\s|$)', df_output).group(1)
                        destination_type = "硬盘"
                    elif re.search(r'/dev/sd[a-z][0-9]+', df_output):
                        write_destination = re.search(r'(/dev/sd[a-z][0-9]+)(?:\s|$)', df_output).group(1)
                        destination_type = "硬盘分区"
                elif "/dev/md" in df_output:
                    write_destination = re.search(r'(/dev/md[0-9]+)(?:\s|$)', df_output).group(1)
                    destination_type = "raid块设备"
                elif "/volume" in df_output:
                    write_destination = re.search(r'(\/volume[0-9]*)(?:\s|$)', df_output).group(1)
                    destination_type = "文件系统"

                if write_destination != "未知":
                    write_destination = f"{destination_type}：{write_destination}"
            except Exception as e:
                print(f"检查目录底层设备时出错: {e}")

    except Exception as e:
        print(f"检测系统信息时出错: {e}")

    return system_type, system_version, write_destination


# 检查是否为块设备
def is_block_device(path):
    return path.startswith("/dev/") and os.path.exists(path) and not os.path.isdir(path)


# 获取系统信息
system_type, system_version, write_destination = detect_system_info()
block_size = args.bs

print(f"系统类型: {system_type}")
print(f"系统版本: {system_version}")
print(f"写入目的地: {write_destination}")
print(f"块大小: {block_size}")

# 在脚本运行的当前目录创建以当前日期命名的目录
current_date = datetime.now().strftime('%Y%m%d')
current_dir = os.getcwd()  # 获取脚本运行的当前目录
daily_output_dir = os.path.join(current_dir, current_date)
os.makedirs(daily_output_dir, exist_ok=True)
print(f"创建日期目录: {daily_output_dir}")

# 文件路径更新为当前目录下的日期目录中的文件
log_file = os.path.join(daily_output_dir, f"speed_log-{device_name}.txt")
report_file = os.path.join(daily_output_dir, f"speed_report-{device_name}.html")
run_time = args.run_time

# 确定是对块设备直接测试还是在目录中创建文件测试
is_direct_device_test = is_block_device(args.output_dir)

# 如果是目录测试，需要创建目录并准备文件
if not is_direct_device_test:
    # 确保输出目录存在
    try:
        os.makedirs(args.output_dir, exist_ok=True)
        output_dir = args.output_dir
    except Exception as e:
        print(f"创建输出目录失败: {e}")
        sys.exit(1)

    # 文件大小列表（单位GB）
    file_sizes_gb = [20, 50, 100, 200]
else:
    # 如果是直接对块设备测试，使用单一固定大小，避免损坏设备
    output_dir = None
    # 对块设备测试时不实际写入，而是测试固定数量的块
    # 默认测试10GB数据，以保护设备
    test_size_gb = 10


def get_dd_command(output_target, size_bytes=None, count=None):
    bs_value = args.bs
    bs_unit = bs_value[-1].lower()  # 获取单位(k, m)
    bs_number = int(bs_value[:-1])  # 获取数值

    if bs_unit == 'k':
        bs_bytes = bs_number * 1024
    elif bs_unit == 'm':
        bs_bytes = bs_number * 1024 * 1024
    else:
        # 默认使用1M
        bs_bytes = 1024 * 1024
        bs_value = "1M"

    if is_direct_device_test:
        # 直接对块设备测试，计算count，并添加iflag=count_bytes以确保不超过指定大小
        if count is None:
            # 如果未指定count，则根据test_size_gb计算
            count = (test_size_gb * 1024 * 1024 * 1024) // bs_bytes

        return [
            "dd",
            "if=/dev/zero",
            f"of={output_target}",
            f"bs={bs_value}",
            f"count={count}",
            "oflag=direct",
            "status=progress"
        ]
    else:
        # 对文件测试
        if size_bytes is not None:
            count = size_bytes // bs_bytes

        return [
            "dd",
            "if=/dev/zero",
            f"of={output_target}",
            f"bs={bs_value}",
            f"count={count}",
            "oflag=direct",
            "status=progress"
        ]


def get_available_space(path):
    try:
        return psutil.disk_usage(path).free
    except:
        # 对于块设备，无法直接获取可用空间
        return float('inf')  # 返回无限大，表示不检查空间


def clear_directory(path):
    if not os.path.isdir(path):
        return  # 如果不是目录，直接返回

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"删除文件失败: {file_path}, 错误: {e}")


# 读取历史数据
speed_data = []
if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        for line in f:
            match = re.search(r'当前速度：(\d+(\.\d+)?) MB/s', line)
            if match:
                speed_data.append(float(match.group(1)))

global_start_time = time.time()

# 记录系统信息到日志
with open(log_file, 'a') as f:
    f.write(f"{datetime.now()} - 系统类型: {system_type}\n")
    f.write(f"{datetime.now()} - 系统版本: {system_version}\n")
    f.write(f"{datetime.now()} - 写入目的地: {write_destination}\n")
    f.write(f"{datetime.now()} - 块大小: {block_size}\n")
    if is_direct_device_test:
        f.write(f"{datetime.now()} - 测试模式: 直接块设备测试\n")
    else:
        f.write(f"{datetime.now()} - 测试模式: 目录文件测试\n")

# 如果是目录测试，先检查空间
if not is_direct_device_test and output_dir:
    if get_available_space(output_dir) < min(file_sizes_gb) * (1024 ** 3):
        print("初始空间不足，正在清空目录...")
        clear_directory(output_dir)

last_speed = None

try:
    # 外层循环条件：当前总运行时间小于指定的run_time
    while time.time() - global_start_time < run_time:
        if is_direct_device_test:
            # 直接对块设备测试
            round_start_time = time.time()
            round_start_msg = f"{datetime.now()} - [本轮开始] 块设备测试开始时间：{datetime.now()}"
            print(round_start_msg)
            with open(log_file, 'a') as f:
                f.write(round_start_msg + "\n")

            # 安全确认
            print(f"警告: 将直接对{args.output_dir}进行写入测试，这可能会擦除设备上的数据")
            print("以10GB为单位进行测试，确保不写入过多数据")

            dd_command = get_dd_command(args.output_dir)
            print(f"执行命令: {' '.join(dd_command)}")
            process = subprocess.Popen(dd_command, stderr=subprocess.PIPE, text=True)

            # 读取dd的stderr输出
            while True:
                line = process.stderr.readline()
                if not line:
                    break
                match = re.search(r'(\d+(?:\.\d+)?)\s+[A-Za-z]+/s', line)
                if match:
                    speed = float(match.group(1))
                    speed_data.append(speed)
                    speed_log = f"{datetime.now()} - 当前速度：{speed:.2f} MB/s"
                    print(speed_log)
                    with open(log_file, 'a') as f:
                        f.write(speed_log + "\n")

                    # 检测若速度下降>=1MB/s则触发采集iotop和iostat数据
                    if last_speed is not None and (last_speed - speed >= 1.0):
                        try:
                            # 执行iotop命令，直接获取有I/O活动的进程，添加-o选项只显示有I/O的进程
                            iotop_cmd = ["iotop", "-b", "-n", "1", "-d", "2", "-P", "-a", "-k", "-t", "-o"]
                            iotop_result = subprocess.run(iotop_cmd, capture_output=True, text=True, timeout=10)
                            iotop_output = iotop_result.stdout

                            # 记录有I/O活动的进程信息
                            iotop_filtered_log = "iotop进程IO信息（只显示有IO活动的进程）：\n"
                            iotop_filtered_log += iotop_output
                            print(iotop_filtered_log)
                            with open(log_file, 'a') as f:
                                f.write(iotop_filtered_log + "\n")
                        except Exception as e:
                            err_msg = f"执行iotop出错：{e}"
                            print(err_msg)
                            with open(log_file, 'a') as f:
                                f.write(err_msg + "\n")
                        try:
                            # 执行iostat命令，只打印有IO活动的设备行
                            iostat_cmd = ["iostat", "-x", "1", "1"]
                            iostat_result = subprocess.run(iostat_cmd, capture_output=True, text=True, timeout=10)
                            iostat_output = iostat_result.stdout
                            iostat_lines = iostat_output.splitlines()
                            filtered_iostat = []
                            header_found = False
                            for l in iostat_lines:
                                if l.startswith("Device"):
                                    header_found = True
                                    filtered_iostat.append(l)
                                    continue
                                if header_found and l.strip():
                                    parts = l.split()
                                    if len(parts) >= 4:
                                        try:
                                            rps = float(parts[2])
                                            wps = float(parts[3])
                                            if rps > 0 or wps > 0:
                                                filtered_iostat.append(l)
                                        except:
                                            pass
                            if filtered_iostat:
                                iostat_log = "iostat输出：\n" + "\n".join(filtered_iostat)
                                print(iostat_log)
                                with open(log_file, 'a') as f:
                                    f.write(iostat_log + "\n")
                        except Exception as e:
                            err_msg = f"执行iostat出错：{e}"
                            print(err_msg)
                            with open(log_file, 'a') as f:
                                f.write(err_msg + "\n")
                    last_speed = speed
                time.sleep(1)
            process.wait()

            round_end_time = time.time()
            round_duration = round_end_time - round_start_time
            round_end_msg = f"{datetime.now()} - [本轮结束] 测试结束时间：{datetime.now()}，本轮测试时长：{round_duration:.2f} 秒"
            print(round_end_msg)
            with open(log_file, 'a') as f:
                f.write(round_end_msg + "\n")

            # 检查是否已经到了测试总时长
            if time.time() - global_start_time >= run_time:
                break
        else:
            # 目录文件测试
            available_space = get_available_space(output_dir)
            # 每轮开始前，如果剩余空间不足最小要求，则清空
            if available_space < min(file_sizes_gb) * (1024 ** 3):
                print("空间不足，正在清空目录...")
                clear_directory(output_dir)

            for size_gb in file_sizes_gb:
                file_size_bytes = size_gb * (1024 ** 3)
                available_space = get_available_space(output_dir)
                # 如果当前空间不足以写入目标文件，则清空目录后重试
                if available_space < file_size_bytes:
                    print(f"可用空间不足以写入{size_gb}GB文件，正在清空目录...")
                    clear_directory(output_dir)
                    available_space = get_available_space(output_dir)
                    if available_space < file_size_bytes:
                        err_msg = f"错误：清空后空间仍不足以写入{size_gb}GB文件，跳过此文件"
                        print(err_msg)
                        with open(log_file, 'a') as f:
                            f.write(f"{datetime.now()} - {err_msg}\n")
                        continue  # 跳过当前文件

                # 使用完整目标文件大小写入
                actual_file_size = file_size_bytes
                actual_size_gb = actual_file_size / (1024 ** 3)
                output_file = os.path.join(output_dir, f"file_{actual_size_gb:.2f}GB_{int(time.time())}.img")
                round_start_time = time.time()
                round_start_msg = f"{datetime.now()} - [本轮开始] 测试开始时间：{datetime.now()}"
                print(round_start_msg)
                with open(log_file, 'a') as f:
                    f.write(round_start_msg + "\n")

                print(f"开始写入文件 {output_file}，大小：{actual_size_gb:.2f} GB")
                dd_command = get_dd_command(output_file, actual_file_size)
                process = subprocess.Popen(dd_command, stderr=subprocess.PIPE, text=True)

                # 读取dd的stderr输出
                while True:
                    line = process.stderr.readline()
                    if not line:
                        break
                    match = re.search(r'(\d+(?:\.\d+)?)\s+[A-Za-z]+/s', line)
                    if match:
                        speed = float(match.group(1))
                        speed_data.append(speed)
                        speed_log = f"{datetime.now()} - 当前速度：{speed:.2f} MB/s"
                        print(speed_log)
                        with open(log_file, 'a') as f:
                            f.write(speed_log + "\n")
                        # 检测若速度下降>=1MB/s则触发采集iotop和iostat数据
                        if last_speed is not None and (last_speed - speed >= 1.0):
                            try:
                                # 执行iotop命令，直接获取有I/O活动的进程，添加-o选项只显示有I/O的进程
                                iotop_cmd = ["iotop", "-b", "-n", "1", "-d", "2", "-P", "-a", "-k", "-t", "-o"]
                                iotop_result = subprocess.run(iotop_cmd, capture_output=True, text=True, timeout=10)
                                iotop_output = iotop_result.stdout

                                # 记录有I/O活动的进程信息
                                iotop_filtered_log = "iotop进程IO信息（只显示有IO活动的进程）：\n"
                                iotop_filtered_log += iotop_output
                                print(iotop_filtered_log)
                                with open(log_file, 'a') as f:
                                    f.write(iotop_filtered_log + "\n")
                            except Exception as e:
                                err_msg = f"执行iotop出错：{e}"
                                print(err_msg)
                                with open(log_file, 'a') as f:
                                    f.write(err_msg + "\n")
                            try:
                                # 执行iostat命令，只打印有IO活动的设备行
                                iostat_cmd = ["iostat", "-x", "1", "1"]
                                iostat_result = subprocess.run(iostat_cmd, capture_output=True, text=True, timeout=10)
                                iostat_output = iostat_result.stdout
                                iostat_lines = iostat_output.splitlines()
                                filtered_iostat = []
                                header_found = False
                                for l in iostat_lines:
                                    if l.startswith("Device"):
                                        header_found = True
                                        filtered_iostat.append(l)
                                        continue
                                    if header_found and l.strip():
                                        parts = l.split()
                                        if len(parts) >= 4:
                                            try:
                                                rps = float(parts[2])
                                                wps = float(parts[3])
                                                if rps > 0 or wps > 0:
                                                    filtered_iostat.append(l)
                                            except:
                                                pass
                                if filtered_iostat:
                                    iostat_log = "iostat输出：\n" + "\n".join(filtered_iostat)
                                    print(iostat_log)
                                    with open(log_file, 'a') as f:
                                        f.write(iostat_log + "\n")
                            except Exception as e:
                                err_msg = f"执行iostat出错：{e}"
                                print(err_msg)
                                with open(log_file, 'a') as f:
                                    f.write(err_msg + "\n")
                        last_speed = speed
                    time.sleep(1)
                process.wait()
                round_end_time = time.time()
                round_duration = round_end_time - round_start_time
                round_end_msg = f"{datetime.now()} - [本轮结束] 测试结束时间：{datetime.now()}，本轮测试时长：{round_duration:.2f} 秒"
                print(round_end_msg)
                with open(log_file, 'a') as f:
                    f.write(round_end_msg + "\n")
except KeyboardInterrupt:
    print("脚本被中断，生成报告...")
except Exception as e:
    error_msg = f"发生错误: {e}"
    print(error_msg)
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {error_msg}\n")

# 计算当前会话的总运行时长
current_run_time = time.time() - global_start_time
runtime_msg = f"{datetime.now()} - 总运行时间：{current_run_time:.2f} 秒"
print(runtime_msg)
with open(log_file, 'a') as f:
    f.write(runtime_msg + "\n")

# 统计数据计算
max_speed = max(speed_data) if speed_data else 0
min_speed = min(speed_data) if speed_data else 0
avg_speed = statistics.mean(speed_data) if speed_data else 0

# 格式化当前会话测试时长为 xx小时xx分钟xx秒
hours = int(current_run_time // 3600)
minutes = int((current_run_time % 3600) // 60)
seconds = int(current_run_time % 60)
current_run_duration_str = f"最后一轮测试时长：{hours}小时{minutes}分钟{seconds}秒"

# 读取完整日志文件内容用于下载
try:
    with open(log_file, 'r', encoding='utf-8') as f:
        full_log_content = f.read()
except Exception as e:
    full_log_content = f"读取日志文件出错：{e}"

# 将完整日志编码为base64，用于下载功能
try:
    full_log_base64 = base64.b64encode(full_log_content.encode('utf-8')).decode('utf-8')
except Exception as e:
    full_log_base64 = ""
    print(f"编码日志文件出错：{e}")

# 累计计算日志中所有"总运行时间"记录（单位：秒）
cumulative_runtime = 0.0
runtime_pattern = r"总运行时间：([\d\.]+) 秒"
all_runtimes = re.findall(runtime_pattern, full_log_content)
for rt in all_runtimes:
    try:
        cumulative_runtime += float(rt)
    except Exception:
        continue
hours_cum = int(cumulative_runtime // 3600)
minutes_cum = int((cumulative_runtime % 3600) // 60)
seconds_cum = int(cumulative_runtime % 60)
cumulative_runtime_str = f"累计测试时长：{hours_cum}小时{minutes_cum}分钟{seconds_cum}秒"

# 修改HTML报告，添加测试模式
test_mode = "直接块设备测试" if is_direct_device_test else "目录文件测试"

# 简化版的HTML报告，只包含统计数据和下载按钮
html_report = f"""
<html>
<head>
    <meta charset="utf-8">
    <title>dd写入速度测试报告 - 设备: {device_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 0;
        }}
        header {{
            background-color: #004085;
            color: #fff;
            padding: 20px;
            text-align: center;
        }}
        .container {{
            max-width: 800px;
            margin: 20px auto;
            background: #fff;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }}
        h1, h2, h3 {{
            margin: 0 0 15px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #dee2e6;
            padding: 12px;
            text-align: center;
        }}
        th {{
            background-color: #e9ecef;
        }}
        .time-info {{
            margin: 20px 0;
            line-height: 1.6;
        }}
        .system-info {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
            border-left: 4px solid #004085;
        }}
        .system-info p {{
            margin: 5px 0;
            line-height: 1.6;
        }}
        .download-container {{
            display: flex;
            justify-content: center;
            margin-top: 30px;
        }}
        .download-btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            background-color: #28a745;
            color: #fff;
            cursor: pointer;
            font-size: 16px;
            display: flex;
            align-items: center;
            text-decoration: none;
        }}
        .download-btn:hover {{
            background-color: #218838;
        }}
        .download-btn i {{
            margin-right: 8px;
            font-size: 20px;
        }}
        .hidden {{
            display: none;
        }}
        .date-info {{
            text-align: center;
            margin-bottom: 15px;
            color: #666;
        }}
    </style>
</head>
<body>
    <header>
        <h1>dd速度测试报告-写速</h1>
        <h3>测试设备： {device_name}</h3>
        <div class="date-info">测试日期：{current_date}</div>
    </header>
    <div class="container">
        <div class="system-info">
            <h2>系统信息</h2>
            <p><strong>系统类型：</strong> {system_type}</p>
            <p><strong>系统版本：</strong> {system_version}</p>
            <p><strong>写入目的地：</strong> {write_destination}</p>
            <p><strong>测试模式：</strong> {test_mode}</p>
            <p><strong>块大小：</strong> {block_size}</p>
        </div>

        <h2>统计数据</h2>
        <table>
            <tr>
                <th>最大速度 (MB/s)</th>
                <th>最小速度 (MB/s)</th>
                <th>平均速度 (MB/s)</th>
            </tr>
            <tr>
                <td>{max_speed:.2f}</td>
                <td>{min_speed:.2f}</td>
                <td>{avg_speed:.2f}</td>
            </tr>
        </table>

        <div class="time-info">
            <p>{current_run_duration_str}</p>
            <p>{cumulative_runtime_str}</p>
        </div>

        <div class="download-container">
            <a id="downloadBtn" class="download-btn" href="#" download="speed_log-{device_name}.txt">
                <i>📥</i> 下载完整日志
            </a>
        </div>

        <textarea id="fullLogData" class="hidden">{full_log_base64}</textarea>
    </div>

    <script>
    document.addEventListener("DOMContentLoaded", function(){{
        var downloadBtn = document.getElementById("downloadBtn");
        var fullLogData = document.getElementById("fullLogData");

        // 设置下载链接
        if (fullLogData.value) {{
            var dataUri = "data:text/plain;base64," + fullLogData.value;
            downloadBtn.setAttribute("href", dataUri);
        }}
    }});
    </script>
</body>
</html>
"""

with open(report_file, 'w', encoding='utf-8') as f:
    f.write(html_report)

print(f"HTML 报告已生成：{os.path.abspath(report_file)}")