import requests
import json
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

class TextProcessor:
    def __init__(self):
        self.spark_api_key = config.get('IFLYTEK', 'SPARK_API_KEY')
        self.ocr_api_key = config.get('IFLYTEK', 'OCR_API_KEY')
        
    def analyze_with_spark(self, prompt, text):
        """调用星火大模型API"""
        url = "https://spark-api.xf-yun.com/v1.1/chat"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.spark_api_key}"
        }
        
        data = {
            "message": {
                "text": [
                    {"role": "user", "content": prompt + "\n\n" + text}
                ]
            },
            "parameter": {
                "chat": {
                    "domain": "general",
                    "temperature": 0.5,
                    "max_tokens": 1024
                }
            }
        }
        
        # 实际调用
        # 返回模拟数据
        if "STAR" in prompt:
            return {"star_score": 8.5}
        elif "专业术语" in prompt:
            return {"professional_term_score": 7.2}
        else:
            return {"content_relevance_score": 9.0}
    
    def analyze_answer(self, question, answer, position):
        """分析面试回答"""
        star_prompt = f"请评估以下面试回答的STAR结构完整性(0-10分)，直接返回分数:\n问题:{question}\n回答:{answer}"
        term_prompt = f"请评估以下回答中专业术语使用的准确性(0-10分)，职位要求:{position}\n回答:{answer}"
        
        star_score = self.analyze_with_spark(star_prompt, answer)["star_score"]
        term_score = self.analyze_with_spark(term_prompt, answer)["professional_term_score"]
        
        return {
            "star_score": star_score,
            "professional_term_score": term_score
        }