from flask import Blueprint, render_template, jsonify, current_app
import os
from datetime import datetime
import logging

reports = Blueprint('reports', __name__)

@reports.route('/reports')
def list_reports():
    """列出所有报告"""
    try:
        reports_dir = os.path.join('reports')
        if not os.path.exists(reports_dir):
            return render_template('reports.html', reports=[])
            
        reports = []
        for file in os.listdir(reports_dir):
            if file.endswith('.html'):
                file_path = os.path.join(reports_dir, file)
                stat = os.stat(file_path)
                # 使用完整的文件名作为ID
                report_id = file
                reports.append({
                    'id': report_id,
                    'create_time': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                })
                
        # 按创建时间倒序排序
        reports.sort(key=lambda x: x['create_time'], reverse=True)
        return render_template('reports.html', reports=reports)
    except Exception as e:
        current_app.logger.error(f'获取报告列表失败: {str(e)}')
        return render_template('reports.html', reports=[]) 