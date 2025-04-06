"""
钉钉通知工具
作者: longshen
"""

import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
import os
from datetime import datetime

class DingTalkNotifier:
    """
    钉钉群机器人通知工具
    支持文本、Markdown等多种格式消息
    """
    
    def __init__(self, webhook_url=None, secret=None):
        """
        初始化钉钉通知器
        
        参数:
            webhook_url: 钉钉机器人的webhook地址
            secret: 钉钉机器人的安全设置密钥
        """
        self.webhook_url = webhook_url
        self.secret = secret
        
        # 尝试从环境变量获取配置
        if not self.webhook_url:
            self.webhook_url = os.environ.get('DINGTALK_WEBHOOK_URL')
        
        if not self.secret:
            self.secret = os.environ.get('DINGTALK_SECRET')
    
    def _get_signed_url(self):
        """
        使用密钥进行签名，生成带签名的URL
        
        返回:
            带签名的完整URL
        """
        if not self.secret:
            return self.webhook_url
            
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        
        signed_url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
        return signed_url
    
    def send_text(self, content, at_mobiles=None, at_all=False):
        """
        发送文本消息
        
        参数:
            content: 消息内容
            at_mobiles: 需要@的手机号列表
            at_all: 是否@所有人
            
        返回:
            响应对象
        """
        if not self.webhook_url:
            return {"errcode": -1, "errmsg": "webhook URL not configured"}
            
        data = {
            "msgtype": "text",
            "text": {"content": content},
            "at": {
                "atMobiles": at_mobiles if at_mobiles else [],
                "isAtAll": at_all
            }
        }
        
        return self._send_request(data)
    
    def send_markdown(self, title, text, at_mobiles=None, at_all=False):
        """
        发送Markdown格式消息
        
        参数:
            title: 消息标题
            text: Markdown格式的消息内容
            at_mobiles: 需要@的手机号列表
            at_all: 是否@所有人
            
        返回:
            响应对象
        """
        if not self.webhook_url:
            return {"errcode": -1, "errmsg": "webhook URL not configured"}
            
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {
                "atMobiles": at_mobiles if at_mobiles else [],
                "isAtAll": at_all
            }
        }
        
        return self._send_request(data)
    
    def send_test_report(self, report_info):
        """
        发送测试报告通知
        
        参数:
            report_info: 包含报告信息的字典，需包含以下字段:
                - name: 报告名称
                - status: 测试状态 (成功/失败)
                - modules: 测试的模块列表
                - executor: 执行人
                - report_url: 报告URL
                - total_cases: 测试用例总数
                - passed_cases: 通过用例数
                - failed_cases: 失败用例数
                - duration: 持续时间(秒)
        
        返回:
            响应对象
        """
        status_emoji = "✅" if report_info.get('status') == '成功' else "❌"
        
        # 计算通过率
        total = int(report_info.get('total_cases', 0))
        passed = int(report_info.get('passed_cases', 0))
        pass_rate = f"{(passed / total * 100) if total > 0 else 0:.1f}%"
        
        # 格式化持续时间
        duration_seconds = int(report_info.get('duration', 0))
        minutes, seconds = divmod(duration_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        duration_str = f"{hours}小时{minutes}分钟{seconds}秒" if hours > 0 else f"{minutes}分钟{seconds}秒"
        
        # 构建Markdown格式的消息
        title = f"测试报告: {report_info.get('name', '未命名')} - {status_emoji}"
        
        text = f"""## {status_emoji} 测试报告: {report_info.get('name', '未命名')}

### 📊 测试概况
- **状态**: {status_emoji} {report_info.get('status', '未知')}
- **执行人**: {report_info.get('executor', '系统')}
- **执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **持续时间**: {duration_str}

### 📈 测试数据
- **用例总数**: {report_info.get('total_cases', '0')}
- **通过用例**: {report_info.get('passed_cases', '0')}
- **失败用例**: {report_info.get('failed_cases', '0')}
- **通过率**: {pass_rate}

### 🔍 测试模块
{', '.join(report_info.get('modules', ['未指定']))}

### 📋 测试结果
[点击查看完整报告]({report_info.get('report_url', '#')})

> 本消息由自动化测试平台生成
> 作者: longshen
"""
        
        return self.send_markdown(title, text)
    
    def _send_request(self, data):
        """
        发送HTTP请求到钉钉Webhook
        
        参数:
            data: 要发送的数据
            
        返回:
            响应对象
        """
        try:
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            url = self._get_signed_url()
            
            response = requests.post(
                url, 
                headers=headers,
                data=json.dumps(data)
            )
            
            return response.json()
        except Exception as e:
            return {"errcode": -1, "errmsg": str(e)}


# 用法示例
if __name__ == "__main__":
    # 通过以下环境变量配置或直接传入参数
    # os.environ["DINGTALK_WEBHOOK_URL"] = "https://oapi.dingtalk.com/robot/send?access_token=xxx"
    # os.environ["DINGTALK_SECRET"] = "SEC000...000"
    
    notifier = DingTalkNotifier()
    
    # 发送文本消息
    # notifier.send_text("这是一条测试消息", at_all=True)
    
    # 发送Markdown消息
    # notifier.send_markdown(
    #    "测试通知", 
    #    "### 自动化测试完成\n> 查看[测试报告](https://example.com)"
    # )
    
    # 发送测试报告
    # report_info = {
    #     "name": "系统接口测试",
    #     "status": "成功",
    #     "modules": ["登录模块", "用户管理", "订单处理"],
    #     "executor": "张三",
    #     "report_url": "https://example.com/reports/123",
    #     "total_cases": 100,
    #     "passed_cases": 98,
    #     "failed_cases": 2,
    #     "duration": 356
    # }
    # notifier.send_test_report(report_info) 