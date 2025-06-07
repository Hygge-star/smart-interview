import base64
import json
import unittest
import requests
import redis
from functools import wraps

# 初始化Redis连接
r = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(key_prefix, ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = func(*args, **kwargs)
            r.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# 使用示例
@cache_result("xunfei_asr")
def call_xunfei_asr(audio_data):
    # API调用代码
    pass
class TestAPI(unittest.TestCase):
    BASE_URL = 'http://localhost:5000'
    
    def test_audio_api(self):
        # 这里应该使用真实的测试音频文件
        response = requests.post(f'{self.BASE_URL}/api/audio_stream', files={
            'audio': ('test.wav', open('test.wav', 'rb'))
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('transcript', response.json())
    
    def test_video_api(self):
        # 这里应该使用真实的测试图像
        with open('test.jpg', 'rb') as f:
            img_data = f.read()
        base64_img = base64.b64encode(img_data).decode('utf-8')
        
        response = requests.post(f'{self.BASE_URL}/api/video_frame', json={
            'frame': f'data:image/jpeg;base64,{base64_img}',
            'timestamp': 123456789
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('analysis', response.json())
    
    def test_text_api(self):
        response = requests.post(f'{self.BASE_URL}/api/analyze_answer', json={
            'question': '请描述一个你遇到的困难问题以及如何解决的',
            'answer': '我在项目中遇到了性能问题...'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('analysis', response.json())

if __name__ == '__main__':
    unittest.main()
