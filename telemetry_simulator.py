#!/usr/bin/env python3
"""
DPU Telemetry 数据模拟器
模拟 BlueField DPU 的网络指标数据
"""

import random
import time
import math
from typing import Dict, Any

class TelemetrySimulator:
    """DPU Telemetry 数据模拟器"""
    
    def __init__(self):
        # 基础参数
        self.base_packets_per_sec = 1000
        self.base_bytes_per_sec = 1000000
        self.base_connections = 100
        self.base_cpu_usage = 30.0
        self.base_memory_usage = 50.0
        
        # 异常模式标志
        self.anomaly_mode = False
        self.anomaly_type = "normal"
        self.anomaly_start_time = 0
        self.anomaly_duration = 30  # 异常持续30秒
        
        # 时间序列数据
        self.time_series = []
        self.max_history = 100
        
        # 初始化历史数据
        self._initialize_history()
    
    def _initialize_history(self):
        """初始化历史数据"""
        current_time = time.time()
        for i in range(self.max_history):
            timestamp = current_time - (self.max_history - i)
            self.time_series.append({
                'timestamp': timestamp,
                'packets_per_sec': self.base_packets_per_sec + random.randint(-100, 100),
                'bytes_per_sec': self.base_bytes_per_sec + random.randint(-100000, 100000),
                'active_connections': self.base_connections + random.randint(-10, 10),
                'dropped_packets': random.randint(0, 5),
                'encryption_hits': random.randint(50, 150),
                'decryption_hits': random.randint(50, 150),
                'cpu_usage': self.base_cpu_usage + random.uniform(-5, 5),
                'memory_usage': self.base_memory_usage + random.uniform(-3, 3),
                'error_count': random.randint(0, 2)
            })
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取当前网络指标"""
        current_time = time.time()
        
        # 检查异常模式是否结束
        if self.anomaly_mode and (current_time - self.anomaly_start_time) > self.anomaly_duration:
            self.anomaly_mode = False
            self.anomaly_type = "normal"
            print("异常模式已结束，恢复正常状态")
        
        # 生成基础指标
        if self.anomaly_mode:
            metrics = self._generate_anomaly_metrics(current_time)
        else:
            metrics = self._generate_normal_metrics(current_time)
        
        # 添加时间戳
        metrics['timestamp'] = current_time
        
        # 更新历史数据
        self.time_series.append(metrics)
        if len(self.time_series) > self.max_history:
            self.time_series.pop(0)
        
        return metrics
    
    def _generate_normal_metrics(self, timestamp: float) -> Dict[str, Any]:
        """生成正常指标"""
        # 添加一些随机波动
        time_factor = math.sin(timestamp / 60) * 0.1  # 每分钟的周期性变化
        
        return {
            'packets_per_sec': int(self.base_packets_per_sec * (1 + time_factor + random.uniform(-0.1, 0.1))),
            'bytes_per_sec': int(self.base_bytes_per_sec * (1 + time_factor + random.uniform(-0.1, 0.1))),
            'active_connections': int(self.base_connections * (1 + time_factor + random.uniform(-0.2, 0.2))),
            'dropped_packets': random.randint(0, 5),
            'encryption_hits': random.randint(50, 150),
            'decryption_hits': random.randint(50, 150),
            'cpu_usage': max(0, min(100, self.base_cpu_usage + random.uniform(-5, 5))),
            'memory_usage': max(0, min(100, self.base_memory_usage + random.uniform(-3, 3))),
            'error_count': random.randint(0, 2)
        }
    
    def _generate_anomaly_metrics(self, timestamp: float) -> Dict[str, Any]:
        """生成异常指标"""
        elapsed = timestamp - self.anomaly_start_time
        intensity = min(1.0, elapsed / 5.0)  # 5秒内达到最大强度
        
        if self.anomaly_type == "ddos":
            return self._generate_ddos_metrics(intensity)
        elif self.anomaly_type == "resource_exhaustion":
            return self._generate_resource_metrics(intensity)
        elif self.anomaly_type == "packet_loss":
            return self._generate_packet_loss_metrics(intensity)
        else:
            return self._generate_normal_metrics(timestamp)
    
    def _generate_ddos_metrics(self, intensity: float) -> Dict[str, Any]:
        """生成DDoS攻击指标"""
        multiplier = 1 + intensity * 10  # 流量增加10倍
        
        return {
            'packets_per_sec': int(self.base_packets_per_sec * multiplier),
            'bytes_per_sec': int(self.base_bytes_per_sec * multiplier),
            'active_connections': int(self.base_connections * multiplier * 2),
            'dropped_packets': int(50 * intensity),
            'encryption_hits': random.randint(50, 150),
            'decryption_hits': random.randint(50, 150),
            'cpu_usage': min(100, self.base_cpu_usage + intensity * 40),
            'memory_usage': min(100, self.base_memory_usage + intensity * 20),
            'error_count': int(10 * intensity)
        }
    
    def _generate_resource_metrics(self, intensity: float) -> Dict[str, Any]:
        """生成资源耗尽指标"""
        return {
            'packets_per_sec': int(self.base_packets_per_sec * (1 - intensity * 0.5)),
            'bytes_per_sec': int(self.base_bytes_per_sec * (1 - intensity * 0.5)),
            'active_connections': int(self.base_connections * (1 - intensity * 0.3)),
            'dropped_packets': int(20 * intensity),
            'encryption_hits': random.randint(50, 150),
            'decryption_hits': random.randint(50, 150),
            'cpu_usage': min(100, self.base_cpu_usage + intensity * 50),
            'memory_usage': min(100, self.base_memory_usage + intensity * 30),
            'error_count': int(20 * intensity)
        }
    
    def _generate_packet_loss_metrics(self, intensity: float) -> Dict[str, Any]:
        """生成丢包异常指标"""
        return {
            'packets_per_sec': int(self.base_packets_per_sec * (1 + intensity * 0.5)),
            'bytes_per_sec': int(self.base_bytes_per_sec * (1 + intensity * 0.5)),
            'active_connections': int(self.base_connections * (1 + intensity * 0.3)),
            'dropped_packets': int(100 * intensity),
            'encryption_hits': random.randint(50, 150),
            'decryption_hits': random.randint(50, 150),
            'cpu_usage': min(100, self.base_cpu_usage + intensity * 20),
            'memory_usage': min(100, self.base_memory_usage + intensity * 10),
            'error_count': int(15 * intensity)
        }
    
    def trigger_anomaly(self, anomaly_type: str = "random"):
        """触发异常场景"""
        if anomaly_type == "random":
            anomaly_types = ["ddos", "resource_exhaustion", "packet_loss"]
            anomaly_type = random.choice(anomaly_types)
        
        self.anomaly_mode = True
        self.anomaly_type = anomaly_type
        self.anomaly_start_time = time.time()
        
        # 新增：通知防御控制器有新的异常
        if hasattr(self, 'defense_controller') and self.defense_controller:
            self.defense_controller.notify_new_anomaly(anomaly_type)
        
        print(f"触发异常场景: {anomaly_type}")
    
    def get_history(self, count: int = 50) -> list:
        """获取历史数据"""
        return self.time_series[-count:] if len(self.time_series) >= count else self.time_series
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.time_series:
            return {}
        
        recent_data = self.time_series[-20:]  # 最近20个数据点
        
        packets = [d['packets_per_sec'] for d in recent_data]
        bytes_data = [d['bytes_per_sec'] for d in recent_data]
        connections = [d['active_connections'] for d in recent_data]
        cpu = [d['cpu_usage'] for d in recent_data]
        
        return {
            'avg_packets_per_sec': sum(packets) / len(packets),
            'avg_bytes_per_sec': sum(bytes_data) / len(bytes_data),
            'avg_connections': sum(connections) / len(connections),
            'avg_cpu_usage': sum(cpu) / len(cpu),
            'max_packets_per_sec': max(packets),
            'min_packets_per_sec': min(packets),
            'anomaly_mode': self.anomaly_mode,
            'anomaly_type': self.anomaly_type
        }

    # 新增：设置防御控制器引用
    def set_defense_controller(self, defense_controller):
        """设置防御控制器引用，用于通知异常触发"""
        self.defense_controller = defense_controller

# 测试代码
if __name__ == "__main__":
    simulator = TelemetrySimulator()
    
    print("正常模式测试:")
    for i in range(5):
        metrics = simulator.get_metrics()
        print(f"时间 {i+1}: PPS={metrics['packets_per_sec']}, CPU={metrics['cpu_usage']:.1f}%")
        time.sleep(1)
    
    print("\n触发DDoS攻击:")
    simulator.trigger_anomaly("ddos")
    for i in range(5):
        metrics = simulator.get_metrics()
        print(f"时间 {i+1}: PPS={metrics['packets_per_sec']}, CPU={metrics['cpu_usage']:.1f}%")
        time.sleep(1) 