import cv2
import numpy as np
import requests
import base64
import json
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

class VideoProcessor:
    def __init__(self):
        self.face_api_key = config.get('IFLYTEK', 'FACE_API_KEY')
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def detect_face(self, frame):
        """使用OpenCV检测人脸"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces
    
    def analyze_emotion(self, face_img):
        """调用讯飞情绪分析API"""
        url = "http://api.xf-yun.com/v1/private/677a6dac"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Host": "api.xf-yun.com"
        }
        
        # 构建请求体
        img_str = base64.b64encode(cv2.imencode('.jpg', face_img)[1]).decode()
        data = {
            "header": {
                "app_id": "your_app_id",
                "status": 3
            },
            "parameter": {
                "677a6dac": {
                    "result": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            },
            "payload": {
                "input1": {
                    "encoding": "jpg",
                    "status": 3,
                    "image": img_str
                }
            }
        }
        
        # 实际调用需要签名处理
        # 此处返回模拟数据
        return {
            "happiness": 0.7,
            "neutral": 0.2,
            "sadness": 0.1,
            "anger": 0.0,
            "fear": 0.0,
            "disgust": 0.0,
            "surprise": 0.0
        }
    
    def detect_eye_contact(self, frame, face_rect):
        """检测眼神接触"""
        x, y, w, h = face_rect
        roi = frame[y:y+h, x:x+w]
        
        # 简化版眼神接触检测
        center_x = x + w//2
        center_y = y + h//2
        
        # 计算眼睛区域
        eye_region = roi[int(h*0.25):int(h*0.45), int(w*0.1):int(w*0.9)]
        
        # 实际应使用眼睛检测模型
        # 这里返回随机值用于演示
        return np.random.choice(["direct_look", "looking_away"])