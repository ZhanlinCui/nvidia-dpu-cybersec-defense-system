#!/usr/bin/env python3
"""
AI异常检测器
集成LSTM模型进行实时异常预测
"""

import numpy as np
import time
import logging
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import json
import os

# 导入自定义模块
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from ai_engine.models.simple_lstm import AnomalyPredictor, ModelConfig
from ai_engine.training.data_processor import DataProcessor, NetworkMetrics, RealTimeDataProcessor

logger = logging.getLogger(__name__)

@dataclass
class AIAnomalyResult:
    """AI异常检测结果"""
    is_anomaly: bool
    risk_score: float  # 0-100
    confidence: float  # 0-1
    anomaly_type: str
    prediction_score: float  # AI模型预测分数
    features: Dict[str, float]
    timestamp: int
    model_version: str

class AIAnomalyDetector:
    """AI异常检测器"""
    
    def __init__(self, model_path: str = None, config_path: str = None):
        self.model_path = model_path
        self.config = self._load_config(config_path)
        
        # 初始化模型配置
        model_config = ModelConfig(
            input_size=9,
            hidden_size=self.config.get('hidden_size', 64),
            num_layers=self.config.get('num_layers', 2),
            sequence_length=self.config.get('sequence_length', 10),
            dropout=self.config.get('dropout', 0.2)
        )
        
        # 初始化AI预测器
        self.predictor = AnomalyPredictor(model_path=model_path)
        
        # 初始化数据处理器
        self.data_processor = RealTimeDataProcessor(
            sequence_length=model_config.sequence_length,
            update_interval=self.config.get('update_interval', 1.0)
        )
        
        # 预测缓存
        self.prediction_history = deque(maxlen=100)
        
        # 阈值配置
        self.risk_threshold = self.config.get('risk_threshold', 0.7)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.6)
        
        # 线程安全
        self.lock = threading.Lock()
        
        # 模型状态
        self.model_loaded = model_path is not None and os.path.exists(model_path)
        self.model_version = "1.0.0"
        
        logger.info(f"AI Anomaly Detector initialized. Model loaded: {self.model_loaded}")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            'hidden_size': 64,
            'num_layers': 2,
            'sequence_length': 10,
            'dropout': 0.2,
            'risk_threshold': 0.7,
            'confidence_threshold': 0.6,
            'update_interval': 1.0,
            'prediction_window': 10,
            'anomaly_types': {
                'ddos_attack': {'threshold': 0.8, 'weight': 1.0},
                'resource_exhaustion': {'threshold': 0.7, 'weight': 0.8},
                'packet_loss': {'threshold': 0.6, 'weight': 0.6},
                'suspicious_behavior': {'threshold': 0.5, 'weight': 0.7}
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        return default_config
    
    def detect_anomaly(self, metrics: Dict, defense_controller=None) -> AIAnomalyResult:
        """
        检测异常
        Args:
            metrics: 网络指标字典
            defense_controller: 防御控制器（可选）
        Returns:
            AI异常检测结果
        """
        with self.lock:
            # 转换为NetworkMetrics对象
            network_metrics = self._dict_to_metrics(metrics)
            
            # 添加数据到处理器
            sequence = self.data_processor.add_metrics_realtime(network_metrics)
            
            # 如果模型未加载或数据不足，返回基础检测结果
            if not self.model_loaded or sequence is None:
                return self._fallback_detection(metrics)
            
            # AI预测
            prediction_score = self.predictor.predict_anomaly(sequence)
            
            # 计算风险评分
            risk_score = self._calculate_risk_score(prediction_score, metrics)
            
            # 计算置信度
            confidence = self._calculate_confidence(prediction_score, sequence)
            
            # 判断是否为异常
            is_anomaly = risk_score > (self.risk_threshold * 100)
            
            # 分类异常类型
            anomaly_type = self._classify_anomaly(metrics, prediction_score)
            
            # 创建结果
            result = AIAnomalyResult(
                is_anomaly=is_anomaly,
                risk_score=risk_score,
                confidence=confidence,
                anomaly_type=anomaly_type,
                prediction_score=prediction_score,
                features=self._extract_features(metrics),
                timestamp=int(time.time()),
                model_version=self.model_version
            )
            
            # 添加到预测历史
            self.prediction_history.append({
                'timestamp': result.timestamp,
                'prediction_score': prediction_score,
                'risk_score': risk_score,
                'is_anomaly': is_anomaly
            })
            
            return result
    
    def _dict_to_metrics(self, metrics_dict: Dict) -> NetworkMetrics:
        """将字典转换为NetworkMetrics对象"""
        return NetworkMetrics(
            timestamp=metrics_dict.get('timestamp', int(time.time())),
            packets_per_sec=metrics_dict.get('packets_per_sec', 0),
            bytes_per_sec=metrics_dict.get('bytes_per_sec', 0),
            active_connections=metrics_dict.get('active_connections', 0),
            dropped_packets=metrics_dict.get('dropped_packets', 0),
            encryption_hits=metrics_dict.get('encryption_hits', 0),
            decryption_hits=metrics_dict.get('decryption_hits', 0),
            cpu_usage=metrics_dict.get('cpu_usage', 0.0),
            memory_usage=metrics_dict.get('memory_usage', 0.0),
            error_count=metrics_dict.get('error_count', 0)
        )
    
    def _fallback_detection(self, metrics: Dict) -> AIAnomalyResult:
        """基础检测（当AI模型不可用时）"""
        # 简单的基于阈值的检测
        risk_score = 0
        
        if metrics.get('packets_per_sec', 0) > 5000:
            risk_score += 30
        if metrics.get('cpu_usage', 0) > 80:
            risk_score += 25
        if metrics.get('memory_usage', 0) > 90:
            risk_score += 20
        if metrics.get('error_count', 0) > 10:
            risk_score += 15
        if metrics.get('dropped_packets', 0) > 50:
            risk_score += 10
        
        risk_score = min(100, risk_score)
        
        return AIAnomalyResult(
            is_anomaly=risk_score > 50,
            risk_score=risk_score,
            confidence=0.5,  # 基础检测置信度较低
            anomaly_type='unknown',
            prediction_score=risk_score / 100,
            features=self._extract_features(metrics),
            timestamp=int(time.time()),
            model_version='fallback'
        )
    
    def _calculate_risk_score(self, prediction_score: float, metrics: Dict) -> float:
        """计算风险评分"""
        # 基础风险评分（基于AI预测）
        base_score = prediction_score * 100
        
        # 根据具体指标调整评分
        adjustments = []
        
        # 数据包速率异常
        if metrics.get('packets_per_sec', 0) > 5000:
            adjustments.append(20)
        
        # CPU使用率异常
        if metrics.get('cpu_usage', 0) > 80:
            adjustments.append(15)
        
        # 内存使用率异常
        if metrics.get('memory_usage', 0) > 90:
            adjustments.append(15)
        
        # 错误数量异常
        if metrics.get('error_count', 0) > 10:
            adjustments.append(10)
        
        # 计算最终评分
        final_score = base_score + sum(adjustments)
        return min(100, max(0, final_score))
    
    def _calculate_confidence(self, prediction_score: float, sequence: np.ndarray) -> float:
        """计算预测置信度"""
        # 基于预测分数的置信度
        base_confidence = abs(prediction_score - 0.5) * 2  # 0-1
        
        # 基于历史预测的一致性
        if len(self.prediction_history) > 0:
            recent_predictions = [p['prediction_score'] for p in list(self.prediction_history)[-5:]]
            consistency = 1 - np.std(recent_predictions)
            base_confidence = (base_confidence + consistency) / 2
        
        return min(1.0, max(0.0, base_confidence))
    
    def _classify_anomaly(self, metrics: Dict, prediction_score: float) -> str:
        """分类异常类型"""
        anomaly_types = self.config.get('anomaly_types', {})
        
        # 根据指标特征分类
        if metrics.get('packets_per_sec', 0) > 5000 and prediction_score > 0.8:
            return 'ddos_attack'
        elif metrics.get('cpu_usage', 0) > 80 or metrics.get('memory_usage', 0) > 90:
            return 'resource_exhaustion'
        elif metrics.get('dropped_packets', 0) > 50:
            return 'packet_loss'
        elif metrics.get('error_count', 0) > 10:
            return 'suspicious_behavior'
        else:
            return 'unknown'
    
    def _extract_features(self, metrics: Dict) -> Dict[str, float]:
        """提取特征"""
        return {
            'packets_per_sec': float(metrics.get('packets_per_sec', 0)),
            'bytes_per_sec': float(metrics.get('bytes_per_sec', 0)),
            'active_connections': float(metrics.get('active_connections', 0)),
            'dropped_packets': float(metrics.get('dropped_packets', 0)),
            'encryption_hits': float(metrics.get('encryption_hits', 0)),
            'decryption_hits': float(metrics.get('decryption_hits', 0)),
            'cpu_usage': float(metrics.get('cpu_usage', 0)),
            'memory_usage': float(metrics.get('memory_usage', 0)),
            'error_count': float(metrics.get('error_count', 0))
        }
    
    def train_model(self, training_data_path: str = None):
        """训练模型"""
        try:
            if training_data_path and os.path.exists(training_data_path):
                # 从文件加载训练数据
                self.data_processor.load_data(training_data_path)
            else:
                # 使用当前收集的数据
                pass
            
            # 获取训练数据
            train_seq, train_labels, val_seq, val_labels = self.data_processor.get_training_data()
            
            if len(train_seq) == 0:
                logger.warning("No training data available")
                return False
            
            # 训练模型
            history = self.predictor.train(train_seq, train_labels, val_seq, val_labels)
            
            # 保存模型
            if self.model_path:
                self.predictor.save_model(self.model_path)
                self.model_loaded = True
            
            logger.info("Model training completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
    
    def get_prediction_history(self, window_size: int = 50) -> List[Dict]:
        """获取预测历史"""
        return list(self.prediction_history)[-window_size:]
    
    def get_model_status(self) -> Dict:
        """获取模型状态"""
        return {
            'model_loaded': self.model_loaded,
            'model_version': self.model_version,
            'model_path': self.model_path,
            'data_samples': self.data_processor.get_stats(),
            'prediction_history_size': len(self.prediction_history),
            'config': self.config
        }
    
    def update_thresholds(self, risk_threshold: float = None, confidence_threshold: float = None):
        """更新阈值"""
        if risk_threshold is not None:
            self.risk_threshold = risk_threshold
        if confidence_threshold is not None:
            self.confidence_threshold = confidence_threshold
        
        logger.info(f"Thresholds updated: risk={self.risk_threshold}, confidence={self.confidence_threshold}")

# 测试代码
if __name__ == "__main__":
    # 初始化AI异常检测器
    detector = AIAnomalyDetector()
    
    # 模拟网络指标
    test_metrics = {
        'packets_per_sec': 1200,
        'bytes_per_sec': 1200000,
        'active_connections': 120,
        'dropped_packets': 5,
        'encryption_hits': 120,
        'decryption_hits': 120,
        'cpu_usage': 55.0,
        'memory_usage': 65.0,
        'error_count': 3
    }
    
    # 检测异常
    result = detector.detect_anomaly(test_metrics)
    print(f"Detection Result: {result}")
    
    # 获取模型状态
    status = detector.get_model_status()
    print(f"Model Status: {status}") 