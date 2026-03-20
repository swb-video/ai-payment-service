#!/usr/bin/env python3
"""
Vercel Serverless API - 支付回调处理
"""
import json
import os
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler
from datetime import datetime

# 虎皮椒配置
HUPJ_APP_ID = os.environ.get('HUPJ_APP_ID', '')
HUPJ_APP_SECRET = os.environ.get('HUPJ_APP_SECRET', '')

# 飞书配置
FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID', '')
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET', '')
FEISHU_TABLE_TOKEN = os.environ.get('FEISHU_TABLE_TOKEN', '')


def verify_sign(params, app_secret):
    """验证虎皮椒签名"""
    if 'hash' not in params:
        return False
    
    received_hash = params.pop('hash')
    
    # 按key排序并拼接
    sorted_params = sorted(params.items())
    sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
    sign_str += app_secret
    
    # MD5加密
    calculated_hash = hashlib.md5(sign_str.encode()).hexdigest()
    
    return calculated_hash == received_hash


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Handler"""
    
    def do_GET(self):
        """处理GET请求 - 支付成功页面"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>支付成功</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0;
                }
                .success-card {
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 400px;
                    width: 90%;
                }
                .success-icon {
                    width: 80px;
                    height: 80px;
                    background: #52c41a;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 20px;
                    font-size: 40px;
                    color: white;
                }
                h1 {
                    color: #333;
                    margin: 0 0 10px;
                }
                p {
                    color: #666;
                    margin: 0 0 30px;
                }
                .btn {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 30px;
                    border: none;
                    border-radius: 25px;
                    font-size: 16px;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                }
            </style>
        </head>
        <body>
            <div class="success-card">
                <div class="success-icon">✓</div>
                <h1>支付成功！</h1>
                <p>感谢您的购买，我们将尽快为您处理订单。</p>
                <a href="/" class="btn">返回首页</a>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def do_POST(self):
        """处理POST请求 - 支付回调"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            # 解析回调数据
            params = json.loads(post_data.decode())
            
            print(f"[回调] 收到支付通知: {json.dumps(params, ensure_ascii=False)}")
            
            # 验证签名
            if not verify_sign(params.copy(), HUPJ_APP_SECRET):
                print("[回调] 签名验证失败")
                self._send_response({'code': 1, 'msg': '签名验证失败'})
                return
            
            # 获取订单信息
            order_id = params.get('trade_order_id')
            status = params.get('status')
            
            print(f"[回调] 订单: {order_id}, 状态: {status}")
            
            # TODO: 更新飞书表格订单状态
            # 这里可以添加更新飞书的代码
            
            # 返回成功响应
            self._send_response({'code': 0, 'msg': 'success'})
            
        except Exception as e:
            print(f"[回调] 处理异常: {e}")
            self._send_response({'code': 1, 'msg': str(e)})
    
    def _send_response(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
