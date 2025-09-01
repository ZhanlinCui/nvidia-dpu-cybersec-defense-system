#!/usr/bin/env python3
"""
简单的LSTM异常检测模型
用于网络流量异常预测
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
import time

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """模型配置"""
    input_size: int = 9  # 特征数量
    hidden_size: int = 64
    num_layers: int = 2
    output_size: int = 1  # 异常分数
    sequence_length: int = 10  # 时间序列长度
    dropout: float = 0.2
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100

class SimpleLSTM(nn.Module):
    """简单的LSTM模型"""
    
    def __init__(self, input_size=9, hidden_size=64, num_layers=2, output_size=1, dropout=0.2):
        super(SimpleLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]
        output = self.fc(last_output)
        return self.sigmoid(output)

class AnomalyPredictor:
    """异常预测器"""
    
    def __init__(self, model_path: str = None, device: str = 'cpu'):
        self.device = device
        self.model = SimpleLSTM().to(device)
        self.model_version = "1.0"
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            logger.info(f"Model loaded from {model_path}")
        else:
            logger.warning(f"Model file not found: {model_path}")
        
        logger.info(f"AnomalyPredictor initialized on device: {device}")
    
    def load_model(self, model_path: str):
        """加载模型"""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()
            logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    def predict_anomaly(self, sequence: np.ndarray) -> float:
        """预测异常概率"""
        with torch.no_grad():
            sequence_tensor = torch.FloatTensor(sequence).unsqueeze(0).to(self.device)
            prediction = self.model(sequence_tensor)
            return prediction.item()
    
    def predict_future_anomalies(self, historical_data: List[np.ndarray], 
                               prediction_hours: int = 24) -> Dict:
        """预测未来异常情况"""
        if len(historical_data) < 10:
            return {"error": "Insufficient historical data"}
        
        predictions = []
        current_sequence = historical_data[-10:]  # 使用最近10个时间点的数据
        
        for hour in range(prediction_hours):
            # 预测下一个时间点的异常概率
            anomaly_prob = self.predict_anomaly(np.array(current_sequence))
            
            # 生成下一个时间点的预测数据（基于历史趋势）
            if len(historical_data) > 1:
                # 简单的线性外推
                last_data = historical_data[-1]
                second_last_data = historical_data[-2]
                trend = last_data - second_last_data
                next_data = last_data + trend * 0.1  # 小步长外推
            else:
                next_data = current_sequence[-1]
            
            predictions.append({
                'hour': hour + 1,
                'anomaly_probability': anomaly_prob,
                'risk_level': self._get_risk_level(anomaly_prob),
                'timestamp': int(time.time()) + hour * 3600
            })
            
            # 更新序列（移除最早的数据，添加预测数据）
            current_sequence = current_sequence[1:] + [next_data]
        
        return {
            'predictions': predictions,
            'prediction_hours': prediction_hours,
            'confidence': self._calculate_prediction_confidence(historical_data),
            'trend': self._analyze_trend(predictions)
        }
    
    def _get_risk_level(self, probability: float) -> str:
        """根据概率确定风险等级"""
        if probability < 0.3:
            return "low"
        elif probability < 0.6:
            return "medium"
        else:
            return "high"
    
    def _calculate_prediction_confidence(self, historical_data: List[np.ndarray]) -> float:
        """计算预测置信度"""
        if len(historical_data) < 20:
            return 0.5
        
        # 基于历史数据的稳定性计算置信度
        recent_data = historical_data[-20:]
        variances = []
        for i in range(len(recent_data[0])):
            values = [data[i] for data in recent_data]
            variance = np.var(values)
            variances.append(variance)
        
        avg_variance = np.mean(variances)
        # 方差越小，置信度越高
        confidence = max(0.1, 1.0 - avg_variance / 100)
        return min(0.95, confidence)
    
    def _analyze_trend(self, predictions: List[Dict]) -> Dict:
        """分析预测趋势"""
        if len(predictions) < 2:
            return {"trend": "stable", "direction": "none"}
        
        probs = [p['anomaly_probability'] for p in predictions]
        
        # 计算趋势
        if len(probs) >= 3:
            # 使用线性回归计算趋势
            x = np.arange(len(probs))
            slope = np.polyfit(x, probs, 1)[0]
            
            if slope > 0.01:
                trend = "increasing"
                direction = "up"
            elif slope < -0.01:
                trend = "decreasing"
                direction = "down"
            else:
                trend = "stable"
                direction = "none"
        else:
            trend = "stable"
            direction = "none"
        
        return {
            "trend": trend,
            "direction": direction,
            "slope": slope if len(probs) >= 3 else 0
        }

def create_sample_data(num_samples: int = 1000, sequence_length: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """
    创建示例数据用于测试
    Args:
        num_samples: 样本数量
        sequence_length: 序列长度
    Returns:
        数据和标签
    """
    # 生成正常数据
    normal_data = np.random.normal(0, 1, (num_samples, sequence_length, 9))
    normal_labels = np.zeros((num_samples, 1))
    
    # 生成异常数据 (20% 的样本)
    num_anomalies = num_samples // 5
    anomaly_indices = np.random.choice(num_samples, num_anomalies, replace=False)
    
    for idx in anomaly_indices:
        # 在序列的某个时间点引入异常
        anomaly_time = np.random.randint(0, sequence_length)
        normal_data[idx, anomaly_time, :] += np.random.normal(3, 1, 9)
        normal_labels[idx, 0] = 1
    
    return normal_data, normal_labels

if __name__ == "__main__":
    # 测试代码
    config = ModelConfig()
    predictor = AnomalyPredictor()
    
    # 创建示例数据
    train_data, train_labels = create_sample_data(1000, config.sequence_length)
    val_data, val_labels = create_sample_data(200, config.sequence_length)
    
    # 训练模型
    history = predictor.train(train_data, train_labels, val_data, val_labels)
    
    # 保存模型
    predictor.save_model("models/anomaly_lstm.pth")
    
    # 测试预测
    test_data, _ = create_sample_data(10, config.sequence_length)
    predictions = predictor.predict(test_data)
    print(f"Predictions: {predictions.flatten()}") 