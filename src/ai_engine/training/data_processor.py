#!/usr/bin/env python3
"""
数据预处理模块
用于准备AI模型训练数据
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from collections import deque
import json
import logging
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class NetworkMetrics:
    """网络指标数据结构"""
    timestamp: int
    packets_per_sec: int
    bytes_per_sec: int
    active_connections: int
    dropped_packets: int
    encryption_hits: int
    decryption_hits: int
    cpu_usage: float
    memory_usage: float
    error_count: int

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, sequence_length: int = 10, feature_names: List[str] = None):
        self.sequence_length = sequence_length
        self.feature_names = feature_names or [
            'packets_per_sec', 'bytes_per_sec', 'active_connections',
            'dropped_packets', 'encryption_hits', 'decryption_hits',
            'cpu_usage', 'memory_usage', 'error_count'
        ]
        
        # 数据缓存
        self.data_buffer = deque(maxlen=1000)
        
        # 统计信息
        self.stats = {
            'total_samples': 0,
            'anomaly_samples': 0,
            'normal_samples': 0
        }
        
        logger.info(f"DataProcessor initialized with sequence_length={sequence_length}")
    
    def add_metrics(self, metrics: NetworkMetrics, is_anomaly: bool = False):
        """
        添加网络指标数据
        Args:
            metrics: 网络指标
            is_anomaly: 是否为异常数据
        """
        # 转换为特征向量
        features = self._extract_features(metrics)
        
        # 添加到缓存
        self.data_buffer.append({
            'features': features,
            'timestamp': metrics.timestamp,
            'is_anomaly': is_anomaly
        })
        
        # 更新统计信息
        self.stats['total_samples'] += 1
        if is_anomaly:
            self.stats['anomaly_samples'] += 1
        else:
            self.stats['normal_samples'] += 1
    
    def _extract_features(self, metrics: NetworkMetrics) -> np.ndarray:
        """提取特征向量"""
        features = [
            metrics.packets_per_sec,
            metrics.bytes_per_sec,
            metrics.active_connections,
            metrics.dropped_packets,
            metrics.encryption_hits,
            metrics.decryption_hits,
            metrics.cpu_usage,
            metrics.memory_usage,
            metrics.error_count
        ]
        return np.array(features, dtype=np.float32)
    
    def create_sequences(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        创建时间序列数据
        Returns:
            序列数据和标签
        """
        if len(self.data_buffer) < self.sequence_length:
            logger.warning(f"Not enough data: {len(self.data_buffer)} < {self.sequence_length}")
            return np.array([]), np.array([])
        
        sequences = []
        labels = []
        
        # 创建滑动窗口序列
        for i in range(len(self.data_buffer) - self.sequence_length + 1):
            sequence_data = []
            sequence_anomaly = False
            
            # 收集序列数据
            for j in range(self.sequence_length):
                data_point = self.data_buffer[i + j]
                sequence_data.append(data_point['features'])
                if data_point['is_anomaly']:
                    sequence_anomaly = True
            
            sequences.append(sequence_data)
            labels.append(1.0 if sequence_anomaly else 0.0)
        
        return np.array(sequences), np.array(labels).reshape(-1, 1)
    
    def create_sequences_with_labels(self, anomaly_threshold: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        创建带标签的时间序列数据
        Args:
            anomaly_threshold: 异常阈值
        Returns:
            序列数据和标签
        """
        if len(self.data_buffer) < self.sequence_length:
            return np.array([]), np.array([])
        
        sequences = []
        labels = []
        
        # 创建滑动窗口序列
        for i in range(len(self.data_buffer) - self.sequence_length + 1):
            sequence_data = []
            anomaly_count = 0
            
            # 收集序列数据
            for j in range(self.sequence_length):
                data_point = self.data_buffer[i + j]
                sequence_data.append(data_point['features'])
                if data_point['is_anomaly']:
                    anomaly_count += 1
            
            # 计算异常比例
            anomaly_ratio = anomaly_count / self.sequence_length
            label = 1.0 if anomaly_ratio >= anomaly_threshold else 0.0
            
            sequences.append(sequence_data)
            labels.append(label)
        
        return np.array(sequences), np.array(labels).reshape(-1, 1)
    
    def get_training_data(self, train_ratio: float = 0.8) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        获取训练和验证数据
        Args:
            train_ratio: 训练数据比例
        Returns:
            训练数据、训练标签、验证数据、验证标签
        """
        sequences, labels = self.create_sequences()
        
        if len(sequences) == 0:
            return np.array([]), np.array([]), np.array([]), np.array([])
        
        # 随机打乱数据
        indices = np.random.permutation(len(sequences))
        sequences = sequences[indices]
        labels = labels[indices]
        
        # 分割训练和验证数据
        split_idx = int(len(sequences) * train_ratio)
        
        train_sequences = sequences[:split_idx]
        train_labels = labels[:split_idx]
        val_sequences = sequences[split_idx:]
        val_labels = labels[split_idx:]
        
        logger.info(f"Training data: {len(train_sequences)}, Validation data: {len(val_sequences)}")
        
        return train_sequences, train_labels, val_sequences, val_labels
    
    def save_data(self, filepath: str):
        """保存数据到文件"""
        data = {
            'sequences': [seq.tolist() for seq in self.data_buffer],
            'stats': self.stats,
            'feature_names': self.feature_names,
            'sequence_length': self.sequence_length
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data saved to {filepath}")
    
    def load_data(self, filepath: str):
        """从文件加载数据"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.data_buffer = deque(data['sequences'], maxlen=1000)
        self.stats = data['stats']
        self.feature_names = data['feature_names']
        self.sequence_length = data['sequence_length']
        
        logger.info(f"Data loaded from {filepath}")
    
    def get_stats(self) -> Dict:
        """获取数据统计信息"""
        return self.stats.copy()
    
    def clear_data(self):
        """清空数据缓存"""
        self.data_buffer.clear()
        self.stats = {
            'total_samples': 0,
            'anomaly_samples': 0,
            'normal_samples': 0
        }
        logger.info("Data cache cleared")

class RealTimeDataProcessor(DataProcessor):
    """实时数据处理器"""
    
    def __init__(self, sequence_length: int = 10, update_interval: float = 1.0):
        super().__init__(sequence_length)
        self.update_interval = update_interval
        self.last_update = time.time()
        
        # 实时预测缓存
        self.prediction_cache = deque(maxlen=100)
        
    def add_metrics_realtime(self, metrics: NetworkMetrics, is_anomaly: bool = False):
        """实时添加指标数据"""
        self.add_metrics(metrics, is_anomaly)
        
        # 检查是否需要更新
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self.last_update = current_time
            return self.get_latest_sequence()
        
        return None
    
    def get_latest_sequence(self) -> Optional[np.ndarray]:
        """获取最新的序列数据用于预测"""
        if len(self.data_buffer) < self.sequence_length:
            return None
        
        # 获取最新的序列
        latest_sequence = []
        for i in range(len(self.data_buffer) - self.sequence_length, len(self.data_buffer)):
            latest_sequence.append(self.data_buffer[i]['features'])
        
        return np.array(latest_sequence)
    
    def add_prediction(self, prediction: float, timestamp: int = None):
        """添加预测结果到缓存"""
        if timestamp is None:
            timestamp = int(time.time())
        
        self.prediction_cache.append({
            'prediction': prediction,
            'timestamp': timestamp
        })
    
    def get_prediction_history(self, window_size: int = 50) -> List[Dict]:
        """获取预测历史"""
        return list(self.prediction_cache)[-window_size:]

def create_synthetic_data(num_samples: int = 1000, anomaly_ratio: float = 0.2) -> Tuple[np.ndarray, np.ndarray]:
    """
    创建合成数据用于测试
    Args:
        num_samples: 样本数量
        anomaly_ratio: 异常数据比例
    Returns:
        序列数据和标签
    """
    processor = DataProcessor(sequence_length=10)
    
    # 生成正常数据
    normal_samples = int(num_samples * (1 - anomaly_ratio))
    for i in range(normal_samples):
        metrics = NetworkMetrics(
            timestamp=int(time.time()) + i,
            packets_per_sec=np.random.normal(1000, 200),
            bytes_per_sec=np.random.normal(1000000, 200000),
            active_connections=np.random.normal(100, 20),
            dropped_packets=np.random.normal(5, 2),
            encryption_hits=np.random.normal(100, 20),
            decryption_hits=np.random.normal(100, 20),
            cpu_usage=np.random.normal(50, 10),
            memory_usage=np.random.normal(60, 10),
            error_count=np.random.normal(3, 1)
        )
        processor.add_metrics(metrics, is_anomaly=False)
    
    # 生成异常数据
    anomaly_samples = num_samples - normal_samples
    for i in range(anomaly_samples):
        metrics = NetworkMetrics(
            timestamp=int(time.time()) + normal_samples + i,
            packets_per_sec=np.random.normal(5000, 1000),  # 异常高
            bytes_per_sec=np.random.normal(5000000, 1000000),  # 异常高
            active_connections=np.random.normal(500, 100),  # 异常高
            dropped_packets=np.random.normal(50, 10),  # 异常高
            encryption_hits=np.random.normal(500, 100),  # 异常高
            decryption_hits=np.random.normal(500, 100),  # 异常高
            cpu_usage=np.random.normal(90, 5),  # 异常高
            memory_usage=np.random.normal(95, 3),  # 异常高
            error_count=np.random.normal(20, 5)  # 异常高
        )
        processor.add_metrics(metrics, is_anomaly=True)
    
    return processor.create_sequences()

if __name__ == "__main__":
    # 测试代码
    processor = DataProcessor(sequence_length=10)
    
    # 创建合成数据
    sequences, labels = create_synthetic_data(1000, 0.2)
    print(f"Generated {len(sequences)} sequences with {np.sum(labels)} anomalies")
    
    # 获取训练数据
    train_seq, train_labels, val_seq, val_labels = processor.get_training_data()
    print(f"Training: {len(train_seq)}, Validation: {len(val_seq)}")
    
    # 保存数据
    processor.save_data("data/network_data.json") 