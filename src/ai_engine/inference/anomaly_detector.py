#!/usr/bin/env python3
"""
AI 异常检测推理服务
基于 TensorRT-Lite 的实时网络异常检测
"""

import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import json
import time
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import deque
import threading
import queue

# 配置日志
logging.basicConfig(level=logging.INFO)
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

@dataclass
class AnomalyResult:
    """异常检测结果"""
    is_anomaly: bool
    risk_score: float  # 0-100
    confidence: float  # 0-1
    anomaly_type: str
    features: Dict[str, float]
    timestamp: int

class TensorRTInferenceEngine:
    """TensorRT 推理引擎"""
    
    def __init__(self, model_path: str, batch_size: int = 1):
        self.model_path = model_path
        self.batch_size = batch_size
        self.engine = None
        self.context = None
        self.stream = None
        self.host_inputs = []
        self.host_outputs = []
        self.device_inputs = []
        self.device_outputs = []
        self.bindings = []
        
        self._load_engine()
        self._create_context()
    
    def _load_engine(self):
        """加载 TensorRT 引擎"""
        logger.info(f"Loading TensorRT engine from {self.model_path}")
        
        with open(self.model_path, 'rb') as f:
            engine_data = f.read()
        
        runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
        self.engine = runtime.deserialize_cuda_engine(engine_data)
        
        logger.info(f"Engine loaded successfully. Max batch size: {self.engine.max_batch_size}")
    
    def _create_context(self):
        """创建推理上下文"""
        self.context = self.engine.create_execution_context()
        self.stream = cuda.Stream()
        
        # 分配内存
        for binding in self.engine:
            size = trt.volume(self.engine.get_binding_shape(binding)) * self.batch_size
            dtype = trt.nptype(self.engine.get_binding_dtype(binding))
            
            # 分配主机和设备内存
            host_mem = cuda.pagelocked_empty(size, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)
            
            self.host_inputs.append(host_mem) if self.engine.binding_is_input(binding) else self.host_outputs.append(host_mem)
            self.device_inputs.append(device_mem) if self.engine.binding_is_input(binding) else self.device_outputs.append(device_mem)
            self.bindings.append(int(device_mem))
    
    def infer(self, input_data: np.ndarray) -> np.ndarray:
        """执行推理"""
        # 复制输入数据到主机内存
        np.copyto(self.host_inputs[0], input_data.ravel())
        
        # 将数据从主机复制到设备
        cuda.memcpy_htod_async(self.device_inputs[0], self.host_inputs[0], self.stream)
        
        # 执行推理
        self.context.execute_async_v2(bindings=self.bindings, stream_handle=self.stream.handle)
        
        # 将结果从设备复制到主机
        cuda.memcpy_dtoh_async(self.host_outputs[0], self.device_outputs[0], self.stream)
        
        # 同步流
        self.stream.synchronize()
        
        return self.host_outputs[0].reshape(self.batch_size, -1)

class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self, model_path: str, config_path: str = None):
        self.model_path = model_path
        self.config = self._load_config(config_path)
        
        # 初始化推理引擎
        self.inference_engine = TensorRTInferenceEngine(model_path)
        
        # 特征窗口 (用于时间序列分析)
        self.feature_window = deque(maxlen=self.config.get('window_size', 10))
        
        # 风险阈值
        self.risk_threshold = self.config.get('risk_threshold', 0.7)
        self.anomaly_threshold = self.config.get('anomaly_threshold', 0.8)
        
        # 线程安全
        self.lock = threading.Lock()
        
        logger.info("Anomaly detector initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            'window_size': 10,
            'risk_threshold': 0.7,
            'anomaly_threshold': 0.8,
            'feature_names': [
                'packets_per_sec', 'bytes_per_sec', 'active_connections',
                'dropped_packets', 'encryption_hits', 'decryption_hits',
                'cpu_usage', 'memory_usage', 'error_count'
            ],
            'normalization': {
                'packets_per_sec': {'mean': 1000, 'std': 500},
                'bytes_per_sec': {'mean': 1000000, 'std': 500000},
                'active_connections': {'mean': 100, 'std': 50},
                'dropped_packets': {'mean': 10, 'std': 5},
                'encryption_hits': {'mean': 100, 'std': 50},
                'decryption_hits': {'mean': 100, 'std': 50},
                'cpu_usage': {'mean': 50, 'std': 20},
                'memory_usage': {'mean': 60, 'std': 20},
                'error_count': {'mean': 5, 'std': 3}
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        return default_config
    
    def _normalize_features(self, metrics: NetworkMetrics) -> np.ndarray:
        """特征标准化"""
        features = []
        norm_config = self.config['normalization']
        
        # 提取特征值
        feature_values = [
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
        
        # 标准化
        for i, (name, value) in enumerate(zip(self.config['feature_names'], feature_values)):
            if name in norm_config:
                mean = norm_config[name]['mean']
                std = norm_config[name]['std']
                normalized = (value - mean) / (std + 1e-8)
                features.append(normalized)
            else:
                features.append(value)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_temporal_features(self, metrics: NetworkMetrics) -> np.ndarray:
        """提取时间序列特征"""
        with self.lock:
            # 添加当前指标到窗口
            self.feature_window.append(metrics)
            
            # 如果窗口未满，使用零填充
            if len(self.feature_window) < self.feature_window.maxlen:
                padding_size = self.feature_window.maxlen - len(self.feature_window)
                for _ in range(padding_size):
                    self.feature_window.appendleft(NetworkMetrics(0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0))
            
            # 构建时间序列特征
            temporal_features = []
            for m in self.feature_window:
                features = self._normalize_features(m)
                temporal_features.extend(features)
            
            return np.array(temporal_features, dtype=np.float32)
    
    def detect_anomaly(self, metrics: NetworkMetrics) -> AnomalyResult:
        """检测异常"""
        start_time = time.time()
        
        try:
            # 提取时间序列特征
            features = self._extract_temporal_features(metrics)
            
            # 重塑为模型输入格式 (batch_size, sequence_length, feature_dim)
            feature_dim = len(self.config['feature_names'])
            sequence_length = self.config['window_size']
            model_input = features.reshape(1, sequence_length, feature_dim)
            
            # 执行推理
            raw_output = self.inference_engine.infer(model_input)
            
            # 解析输出
            anomaly_prob = float(raw_output[0, 0])  # 异常概率
            risk_score = float(raw_output[0, 1]) * 100  # 风险评分 (0-100)
            confidence = float(raw_output[0, 2])  # 置信度
            
            # 判断是否为异常
            is_anomaly = anomaly_prob > self.anomaly_threshold
            
            # 确定异常类型
            anomaly_type = self._classify_anomaly(metrics, risk_score)
            
            # 构建特征字典
            feature_dict = {
                'packets_per_sec': metrics.packets_per_sec,
                'bytes_per_sec': metrics.bytes_per_sec,
                'active_connections': metrics.active_connections,
                'dropped_packets': metrics.dropped_packets,
                'cpu_usage': metrics.cpu_usage,
                'error_count': metrics.error_count
            }
            
            inference_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            logger.info(f"Anomaly detection completed in {inference_time:.2f}ms. "
                       f"Risk: {risk_score:.1f}, Anomaly: {is_anomaly}")
            
            return AnomalyResult(
                is_anomaly=is_anomaly,
                risk_score=risk_score,
                confidence=confidence,
                anomaly_type=anomaly_type,
                features=feature_dict,
                timestamp=metrics.timestamp
            )
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            # 返回默认结果
            return AnomalyResult(
                is_anomaly=False,
                risk_score=0.0,
                confidence=0.0,
                anomaly_type="unknown",
                features={},
                timestamp=metrics.timestamp
            )
    
    def _classify_anomaly(self, metrics: NetworkMetrics, risk_score: float) -> str:
        """分类异常类型"""
        if metrics.dropped_packets > 1000:
            return "packet_loss_attack"
        elif metrics.active_connections > 10000:
            return "connection_flood"
        elif metrics.error_count > 100:
            return "system_error"
        elif metrics.cpu_usage > 80:
            return "resource_exhaustion"
        elif risk_score > 80:
            return "suspicious_behavior"
        else:
            return "normal"
    
    def update_thresholds(self, risk_threshold: float = None, anomaly_threshold: float = None):
        """更新检测阈值"""
        with self.lock:
            if risk_threshold is not None:
                self.risk_threshold = risk_threshold
            if anomaly_threshold is not None:
                self.anomaly_threshold = anomaly_threshold
        
        logger.info(f"Updated thresholds - Risk: {self.risk_threshold}, Anomaly: {self.anomaly_threshold}")

class AnomalyDetectionService:
    """异常检测服务"""
    
    def __init__(self, model_path: str, config_path: str = None):
        self.detector = AnomalyDetector(model_path, config_path)
        self.running = False
        self.metrics_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.processing_thread = None
        
        logger.info("Anomaly detection service initialized")
    
    def start(self):
        """启动服务"""
        if self.running:
            logger.warning("Service is already running")
            return
        
        self.running = True
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.start()
        
        logger.info("Anomaly detection service started")
    
    def stop(self):
        """停止服务"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join()
        
        logger.info("Anomaly detection service stopped")
    
    def _processing_loop(self):
        """处理循环"""
        while self.running:
            try:
                # 从队列获取指标数据
                metrics = self.metrics_queue.get(timeout=1.0)
                
                # 执行异常检测
                result = self.detector.detect_anomaly(metrics)
                
                # 将结果放入结果队列
                self.results_queue.put(result)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Processing error: {e}")
    
    def submit_metrics(self, metrics: NetworkMetrics):
        """提交指标数据"""
        self.metrics_queue.put(metrics)
    
    def get_result(self, timeout: float = 1.0) -> Optional[AnomalyResult]:
        """获取检测结果"""
        try:
            return self.results_queue.get(timeout=timeout)
        except queue.Empty:
            return None

# 使用示例
if __name__ == "__main__":
    # 初始化服务
    service = AnomalyDetectionService(
        model_path="models/anomaly_detector.trt",
        config_path="configs/anomaly_detector.json"
    )
    
    # 启动服务
    service.start()
    
    try:
        # 模拟指标数据
        metrics = NetworkMetrics(
            timestamp=int(time.time()),
            packets_per_sec=1500,
            bytes_per_sec=2000000,
            active_connections=150,
            dropped_packets=50,
            encryption_hits=200,
            decryption_hits=200,
            cpu_usage=65.0,
            memory_usage=70.0,
            error_count=10
        )
        
        # 提交检测
        service.submit_metrics(metrics)
        
        # 获取结果
        result = service.get_result()
        if result:
            print(f"Detection result: {result}")
        
    finally:
        service.stop() 