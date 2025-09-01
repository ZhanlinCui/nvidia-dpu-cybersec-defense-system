#!/usr/bin/env python3
"""
AI 异常检测器 (简化版)
基于规则的异常检测和风险评分
"""

import time
import math
from typing import Dict, Any, List
from collections import deque

class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self):
        # 检测阈值 - 降低阈值使异常更容易被检测
        self.risk_threshold = 30.0  # 从70降到30
        self.anomaly_threshold = 40.0  # 从80降到40
        
        # 特征权重
        self.weights = {
            'packets_per_sec': 0.2,
            'bytes_per_sec': 0.15,
            'active_connections': 0.25,
            'dropped_packets': 0.3,
            'cpu_usage': 0.1
        }
        
        # 历史数据窗口
        self.history_window = deque(maxlen=10)
        
        # 异常类型定义
        self.anomaly_patterns = {
            'ddos_attack': {
                'packets_per_sec_threshold': 5000,
                'connections_threshold': 500,
                'weight': 0.4
            },
            'resource_exhaustion': {
                'cpu_threshold': 80.0,
                'memory_threshold': 85.0,
                'error_threshold': 20,
                'weight': 0.3
            },
            'packet_loss': {
                'dropped_packets_threshold': 50,
                'weight': 0.3
            },
            'suspicious_behavior': {
                'encryption_ratio_threshold': 0.8,
                'weight': 0.2
            }
        }
        
        # 统计信息
        self.detection_stats = {
            'total_detections': 0,
            'false_positives': 0,
            'true_positives': 0,
            'last_detection_time': 0
        }
    
    def detect_anomaly(self, metrics: Dict[str, Any], defense_controller=None) -> Dict[str, Any]:
        """
        检测异常
        """
        current_time = time.time()
        self.history_window.append(metrics)
        risk_score = self._calculate_risk_score(metrics)
        # 新增：防御激活时风险分数降低
        if defense_controller is not None and getattr(defense_controller, 'defense_active', False):
            risk_score = max(risk_score - 60, 0)
        anomaly_type = self._classify_anomaly(metrics, risk_score)
        is_anomaly = risk_score > self.anomaly_threshold
        confidence = self._calculate_confidence(metrics, risk_score)
        if is_anomaly:
            self.detection_stats['total_detections'] += 1
            self.detection_stats['last_detection_time'] = current_time
        return {
            'is_anomaly': is_anomaly,
            'risk_score': risk_score,
            'confidence': confidence,
            'anomaly_type': anomaly_type,
            'timestamp': current_time,
            'features': self._extract_features(metrics)
        }
    
    def _calculate_risk_score(self, metrics: Dict[str, Any]) -> float:
        """计算风险评分 (0-100)"""
        risk_score = 0.0
        
        # 基于丢包率的风险
        if metrics['dropped_packets'] > 20:
            risk_score += 40
        elif metrics['dropped_packets'] > 10:
            risk_score += 25
        elif metrics['dropped_packets'] > 5:
            risk_score += 15
        elif metrics['dropped_packets'] > 2:
            risk_score += 8
        else:
            risk_score += 2  # 基础风险
        
        # 基于连接数的风险
        if metrics['active_connections'] > 500:
            risk_score += 35
        elif metrics['active_connections'] > 200:
            risk_score += 25
        elif metrics['active_connections'] > 100:
            risk_score += 15
        elif metrics['active_connections'] > 50:
            risk_score += 8
        else:
            risk_score += 3  # 基础风险
        
        # 基于CPU使用率的风险
        if metrics['cpu_usage'] > 70:
            risk_score += 30
        elif metrics['cpu_usage'] > 60:
            risk_score += 20
        elif metrics['cpu_usage'] > 50:
            risk_score += 12
        elif metrics['cpu_usage'] > 40:
            risk_score += 6
        else:
            risk_score += 2  # 基础风险
        
        # 基于错误计数的风险
        if metrics['error_count'] > 10:
            risk_score += 35
        elif metrics['error_count'] > 5:
            risk_score += 25
        elif metrics['error_count'] > 2:
            risk_score += 15
        elif metrics['error_count'] > 0:
            risk_score += 8
        else:
            risk_score += 2  # 基础风险
        
        # 基于流量突增的风险
        if len(self.history_window) >= 3:
            recent_avg = sum([h['packets_per_sec'] for h in list(self.history_window)[-3:]]) / 3
            current_pps = metrics['packets_per_sec']
            if current_pps > recent_avg * 2:
                risk_score += 30
            elif current_pps > recent_avg * 1.5:
                risk_score += 20
            elif current_pps > recent_avg * 1.2:
                risk_score += 10
            else:
                risk_score += 3  # 基础风险
        else:
            risk_score += 3  # 基础风险
        
        # 限制最大风险分数
        return min(100.0, risk_score)
    
    def _classify_anomaly(self, metrics: Dict[str, Any], risk_score: float) -> str:
        """分类异常类型"""
        # 首先检查是否真的是异常（基于风险评分）
        if risk_score <= self.anomaly_threshold:
            return "normal"
        
        # DDoS攻击检测
        if (metrics['packets_per_sec'] > self.anomaly_patterns['ddos_attack']['packets_per_sec_threshold'] and
            metrics['active_connections'] > self.anomaly_patterns['ddos_attack']['connections_threshold']):
            return "ddos_attack"
        
        # 资源耗尽检测
        if (metrics['cpu_usage'] > self.anomaly_patterns['resource_exhaustion']['cpu_threshold'] or
            metrics['memory_usage'] > self.anomaly_patterns['resource_exhaustion']['memory_threshold'] or
            metrics['error_count'] > self.anomaly_patterns['resource_exhaustion']['error_threshold']):
            return "resource_exhaustion"
        
        # 丢包异常检测
        if metrics['dropped_packets'] > self.anomaly_patterns['packet_loss']['dropped_packets_threshold']:
            return "packet_loss"
        
        # 可疑行为检测
        if metrics['encryption_hits'] + metrics['decryption_hits'] > 0:
            encryption_ratio = metrics['encryption_hits'] / (metrics['encryption_hits'] + metrics['decryption_hits'])
            if encryption_ratio > self.anomaly_patterns['suspicious_behavior']['encryption_ratio_threshold']:
                return "suspicious_behavior"
        
        # 基于风险评分的通用分类（只有在超过阈值时）
        if risk_score > 90:
            return "critical_anomaly"
        elif risk_score > 80:
            return "high_risk_anomaly"
        elif risk_score > 60:
            return "medium_risk_anomaly"
        elif risk_score > 40:
            return "low_risk_anomaly"
        else:
            return "normal"
    
    def _calculate_confidence(self, metrics: Dict[str, Any], risk_score: float) -> float:
        """计算检测置信度 (0-1)"""
        confidence = 0.5  # 基础置信度
        
        # 基于历史数据的置信度调整
        if len(self.history_window) >= 5:
            recent_anomalies = 0
            for hist in list(self.history_window)[-5:]:
                if self._calculate_risk_score(hist) > self.risk_threshold:
                    recent_anomalies += 1
            
            # 如果最近有多个异常，增加置信度
            if recent_anomalies >= 3:
                confidence += 0.3
            elif recent_anomalies >= 1:
                confidence += 0.1
        
        # 基于风险评分的置信度调整
        if risk_score > 90:
            confidence += 0.3
        elif risk_score > 80:
            confidence += 0.2
        elif risk_score > 70:
            confidence += 0.1
        
        # 基于异常类型的置信度调整
        anomaly_type = self._classify_anomaly(metrics, risk_score)
        if anomaly_type in ['ddos_attack', 'resource_exhaustion']:
            confidence += 0.2
        elif anomaly_type in ['packet_loss', 'suspicious_behavior']:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _extract_features(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """提取特征用于分析"""
        return {
            'packets_per_sec': metrics['packets_per_sec'],
            'bytes_per_sec': metrics['bytes_per_sec'],
            'active_connections': metrics['active_connections'],
            'dropped_packets': metrics['dropped_packets'],
            'cpu_usage': metrics['cpu_usage'],
            'memory_usage': metrics['memory_usage'],
            'error_count': metrics['error_count'],
            'encryption_ratio': (metrics['encryption_hits'] / (metrics['encryption_hits'] + metrics['decryption_hits'] + 1))
        }
    
    def update_thresholds(self, risk_threshold: float = None, anomaly_threshold: float = None):
        """更新检测阈值"""
        if risk_threshold is not None:
            self.risk_threshold = risk_threshold
        if anomaly_threshold is not None:
            self.anomaly_threshold = anomaly_threshold
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取检测统计信息"""
        return {
            'total_detections': self.detection_stats['total_detections'],
            'false_positives': self.detection_stats['false_positives'],
            'true_positives': self.detection_stats['true_positives'],
            'last_detection_time': self.detection_stats['last_detection_time'],
            'current_thresholds': {
                'risk_threshold': self.risk_threshold,
                'anomaly_threshold': self.anomaly_threshold
            },
            'history_size': len(self.history_window)
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        self.detection_stats = {
            'total_detections': 0,
            'false_positives': 0,
            'true_positives': 0,
            'last_detection_time': 0
        }

# 测试代码
if __name__ == "__main__":
    detector = AnomalyDetector()
    
    # 正常数据测试
    normal_metrics = {
        'packets_per_sec': 1000,
        'bytes_per_sec': 1000000,
        'active_connections': 100,
        'dropped_packets': 2,
        'encryption_hits': 100,
        'decryption_hits': 100,
        'cpu_usage': 30.0,
        'memory_usage': 50.0,
        'error_count': 1
    }
    
    result = detector.detect_anomaly(normal_metrics)
    print(f"正常数据检测结果: {result}")
    
    # 异常数据测试
    anomaly_metrics = {
        'packets_per_sec': 8000,
        'bytes_per_sec': 8000000,
        'active_connections': 800,
        'dropped_packets': 100,
        'encryption_hits': 200,
        'decryption_hits': 50,
        'cpu_usage': 85.0,
        'memory_usage': 70.0,
        'error_count': 25
    }
    
    result = detector.detect_anomaly(anomaly_metrics)
    print(f"异常数据检测结果: {result}") 