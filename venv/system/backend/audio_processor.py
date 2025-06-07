import base64
import hashlib
import hmac
import json
import time
from datetime import datetime
from urllib.parse import urlparse, urlencode
import requests
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

class AudioProcessor:
    def __init__(self):
        if config.has_section('IFLYTEK') and config.has_option('IFLYTEK', 'ASR_API_KEY') and config.has_option('IFLYTEK', 'ASR_API_SECRET'):
            self.asr_api_key = config.get('IFLYTEK', 'ASR_API_KEY')
            self.asr_api_secret = config.get('IFLYTEK', 'ASR_API_SECRET')
        else:
            raise ValueError("Missing 'ASR_API_KEY' or 'ASR_API_SECRET' in 'IFLYTEK' section of config.ini")
        self.buffer = b''
        self.last_word_time = datetime.now()
        self.word_count = 0
        
    def transcribe(self, audio_chunk):
        """调用讯飞语音识别API"""
        url = "wss://iat-api.xfyun.cn/v2/iat"
        now = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        signature_origin = f"host: iat-api.xfyun.cn\ndate: {now}\nGET /v2/iat HTTP/1.1"
        signature_sha = hmac.new(
            self.asr_api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization = f'api_key="{self.asr_api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        
        # 实际开发中需使用WebSocket连接
        # 此处简化为模拟返回
        return "这是模拟的语音识别文本", datetime.now().timestamp()
    
    def analyze_speech(self, text, start_time, end_time):
        """分析语速和停顿"""
        duration = end_time - start_time
        words = text.split()
        self.word_count += len(words)
        
        # 计算语速 (字/分钟)
        speech_rate = (len(text) / duration) * 60 if duration > 0 else 0
        
        # 检测停顿 (超过1秒无语音)
        pause_duration = 0
        current_time = datetime.now()
        if (current_time - self.last_word_time).total_seconds() > 1.0:
            pause_duration = (current_time - self.last_word_time).total_seconds()
        
        self.last_word_time = current_time
        
        return {
            "transcript": text,
            "speech_rate": round(speech_rate, 1),
            "pause_duration": round(pause_duration, 1),
            "start_time": start_time,
            "end_time": end_time
        }