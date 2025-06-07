from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit # type: ignore
from audio_processor import AudioProcessor
from video_processor import VideoProcessor 
from text_processor import TextProcessor
import cv2
import numpy as np
import base64
import time

app = Flask(__name__)
app.debug = False
socketio = SocketIO(app, cors_allowed_origins="*")
audio_processor = AudioProcessor()
video_processor = VideoProcessor()
text_processor = TextProcessor()

# 数据结构存储多模态数据
multimodal_data = {
    "audio": [],
    "video": [],
    "text": []
}

@app.route('/api/analyze_resume', methods=['POST'])
def analyze_resume():
    # 简历解析逻辑
    return jsonify({
        "resume_match_score": 85,
        "skills": ["Python", "Flask", "OpenCV"],
        "experience": "5年开发经验"
    })

@socketio.on('audio_stream')
def handle_audio(data):
    """处理实时音频流"""
    audio_chunk = data['audio']
    timestamp = data['timestamp']
    
    # 语音识别
    transcript, end_time = audio_processor.transcribe(audio_chunk)
    
    # 语速分析
    analysis = audio_processor.analyze_speech(transcript, timestamp, end_time)
    
    # 存储结果
    multimodal_data["audio"].append({
        "timestamp": timestamp,
        "data": analysis
    })
    
    # 实时返回结果
    emit('audio_analysis', analysis)

@socketio.on('video_frame')
def handle_video_frame(data):
    """处理视频帧"""
    img_data = base64.b64decode(data['frame'])
    timestamp = data['timestamp']
    
    # 转换为OpenCV格式
    nparr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 人脸检测
    faces = video_processor.detect_face(frame)
    if len(faces) > 0:
        x, y, w, h = faces[0]
        face_img = frame[y:y+h, x:x+w]
        
        # 情绪分析
        emotion = video_processor.analyze_emotion(face_img)
        
        # 眼神接触检测
        gaze_status = video_processor.detect_eye_contact(frame, (x, y, w, h))
        
        # 存储结果
        multimodal_data["video"].append({
            "timestamp": timestamp,
            "data": {
                "emotion": emotion,
                "gaze_status": gaze_status
            }
        })
        
        # 实时返回结果
        emit('video_analysis', {
            "emotion": emotion,
            "gaze_status": gaze_status
        })

@app.route('/api/final_analysis', methods=['POST'])
def final_analysis():
    """面试结束后的综合分析"""
    # 1. 对齐时间戳
    aligned_data = align_timestamps(multimodal_data)
    
    # 2. 添加文本分析
    answers = request.json.get('answers', [])
    position = request.json.get('position', '')
    
    text_analysis = []
    for qa in answers:
        analysis = text_processor.analyze_answer(qa['question'], qa['answer'], position)
        text_analysis.append({
            "question": qa['question'],
            "analysis": analysis
        })
    
    # 3. 构建最终输出
    result = {
        "timeline": aligned_data,
        "summary": {
            "average_speech_rate": calculate_average(aligned_data, 'speech_rate'),
            "eye_contact_ratio": calculate_ratio(aligned_data, 'gaze_status', 'direct_look'),
            "text_analysis": text_analysis,
            "resume_match_score": 85  # 从简历解析获取
        }
    }
    
    return jsonify(result)

def align_timestamps(data):
    """时间戳对齐逻辑"""
    # 简化实现 - 实际应按时间窗口对齐
    aligned = []
    audio_points = data["audio"]
    video_points = data["video"]
    
    for a in audio_points:
        # 找到最近视频点
        closest_video = min(video_points, key=lambda v: abs(v['timestamp'] - a['timestamp']))
        aligned.append({
            "timestamp": a['timestamp'],
            "audio": a['data'],
            "video": closest_video['data']
        })
    
    return aligned

def calculate_average(aligned_data, key):
    """计算aligned_data中指定key的平均值"""
    values = []
    for item in aligned_data:
        audio_data = item.get('audio', {})
        value = audio_data.get(key)
        if isinstance(value, (int, float)):
            values.append(value)
    return sum(values) / len(values) if values else 0

def calculate_ratio(aligned_data, key, target_value):
    """计算某个key等于target_value的比例"""
    count = 0
    total = 0
    for item in aligned_data:
        value = item.get('video', {}).get(key)
        if value is not None:
            total += 1
            if value == target_value:
                count += 1
    return count / total if total > 0 else 0

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)