#!/usr/bin/env python3
"""
AI模型测试脚本
用于测试AI异常检测模型的功能
"""

import os
import sys
import json
import time
import logging
import numpy as np
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_engine.models.simple_lstm import AnomalyPredictor, ModelConfig, create_sample_data
from src.ai_engine.inference.ai_anomaly_detector import AIAnomalyDetector
from src.ai_engine.training.data_processor import DataProcessor, create_synthetic_data

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_model_training():
    """测试模型训练"""
    logger.info("=" * 50)
    logger.info("测试模型训练")
    logger.info("=" * 50)
    
    # 创建模型配置
    config = ModelConfig(
        input_size=9,
        hidden_size=32,  # 减小模型以加快测试
        num_layers=1,
        sequence_length=5,  # 减小序列长度
        dropout=0.2,
        learning_rate=0.001,
        batch_size=16,
        epochs=10  # 减少训练轮数
    )
    
    # 创建预测器
    predictor = AnomalyPredictor(config)
    
    # 生成测试数据
    logger.info("生成测试数据...")
    train_data, train_labels = create_sample_data(100, config.sequence_length)
    val_data, val_labels = create_sample_data(20, config.sequence_length)
    
    logger.info(f"训练数据: {len(train_data)} 样本")
    logger.info(f"验证数据: {len(val_data)} 样本")
    
    # 训练模型
    logger.info("开始训练模型...")
    history = predictor.train(train_data, train_labels, val_data, val_labels)
    
    # 保存模型
    model_path = "models/test_model.pth"
    predictor.save_model(model_path)
    logger.info(f"模型已保存到: {model_path}")
    
    # 测试预测
    test_data, test_labels = create_sample_data(10, config.sequence_length)
    predictions = predictor.predict(test_data)
    
    # 计算准确率
    predicted_labels = (predictions > 0.5).astype(int)
    accuracy = np.mean(predicted_labels == test_labels)
    logger.info(f"测试准确率: {accuracy:.4f}")
    
    return model_path, predictor

def test_ai_detector():
    """测试AI检测器"""
    logger.info("=" * 50)
    logger.info("测试AI检测器")
    logger.info("=" * 50)
    
    # 检查模型文件
    model_path = "models/test_model.pth"
    if not os.path.exists(model_path):
        logger.warning("模型文件不存在，先训练模型...")
        model_path, _ = test_model_training()
    
    # 创建AI检测器，使用与训练时相同的配置
    config_path = "configs/test_ai_config.json"
    
    # 创建测试配置文件
    test_config = {
        'hidden_size': 32,  # 与训练时保持一致
        'num_layers': 1,    # 与训练时保持一致
        'sequence_length': 5,  # 与训练时保持一致
        'dropout': 0.2,
        'risk_threshold': 0.7,
        'confidence_threshold': 0.6,
        'update_interval': 1.0
    }
    
    # 确保配置目录存在
    Path("configs").mkdir(exist_ok=True)
    
    # 保存配置文件
    with open(config_path, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    # 创建AI检测器
    detector = AIAnomalyDetector(model_path=model_path, config_path=config_path)
    
    # 测试正常数据
    normal_metrics = {
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
    
    logger.info("测试正常数据...")
    normal_result = detector.detect_anomaly(normal_metrics)
    logger.info(f"正常数据检测结果:")
    logger.info(f"  风险评分: {normal_result.risk_score:.2f}")
    logger.info(f"  是否异常: {normal_result.is_anomaly}")
    logger.info(f"  置信度: {normal_result.confidence:.2f}")
    logger.info(f"  AI预测分数: {normal_result.prediction_score:.4f}")
    
    # 测试异常数据
    anomaly_metrics = {
        'packets_per_sec': 8000,  # 异常高
        'bytes_per_sec': 8000000,  # 异常高
        'active_connections': 800,  # 异常高
        'dropped_packets': 100,  # 异常高
        'encryption_hits': 800,  # 异常高
        'decryption_hits': 800,  # 异常高
        'cpu_usage': 95.0,  # 异常高
        'memory_usage': 98.0,  # 异常高
        'error_count': 25  # 异常高
    }
    
    logger.info("测试异常数据...")
    anomaly_result = detector.detect_anomaly(anomaly_metrics)
    logger.info(f"异常数据检测结果:")
    logger.info(f"  风险评分: {anomaly_result.risk_score:.2f}")
    logger.info(f"  是否异常: {anomaly_result.is_anomaly}")
    logger.info(f"  置信度: {anomaly_result.confidence:.2f}")
    logger.info(f"  AI预测分数: {anomaly_result.prediction_score:.4f}")
    
    # 获取模型状态
    status = detector.get_model_status()
    logger.info(f"模型状态: {status}")
    
    return detector

def test_data_processor():
    """测试数据处理器"""
    logger.info("=" * 50)
    logger.info("测试数据处理器")
    logger.info("=" * 50)
    
    # 创建数据处理器
    processor = DataProcessor(sequence_length=5)
    
    # 生成合成数据
    logger.info("生成合成数据...")
    sequences, labels = create_synthetic_data(50, 0.3)
    
    logger.info(f"生成序列数: {len(sequences)}")
    logger.info(f"异常样本数: {np.sum(labels)}")
    
    # 获取训练数据
    train_seq, train_labels, val_seq, val_labels = processor.get_training_data()
    
    logger.info(f"训练数据: {len(train_seq)} 样本")
    logger.info(f"验证数据: {len(val_seq)} 样本")
    
    # 测试实时处理
    logger.info("测试实时数据处理...")
    realtime_processor = processor.__class__(sequence_length=5, update_interval=0.1)
    
    # 模拟实时数据流
    for i in range(10):
        metrics = {
            'packets_per_sec': 1000 + i * 100,
            'bytes_per_sec': 1000000 + i * 100000,
            'active_connections': 100 + i * 10,
            'dropped_packets': 5 + i,
            'encryption_hits': 100 + i * 10,
            'decryption_hits': 100 + i * 10,
            'cpu_usage': 50.0 + i * 2,
            'memory_usage': 60.0 + i * 2,
            'error_count': 3 + i
        }
        
        sequence = realtime_processor.add_metrics_realtime(metrics, is_anomaly=(i > 5))
        if sequence is not None:
            logger.info(f"时间步 {i}: 序列形状 {sequence.shape}")
        
        time.sleep(0.1)
    
    return processor

def test_integration():
    """测试集成功能"""
    logger.info("=" * 50)
    logger.info("测试集成功能")
    logger.info("=" * 50)
    
    # 测试模型训练
    model_path, predictor = test_model_training()
    
    # 测试AI检测器
    detector = test_ai_detector()
    
    # 测试数据处理器
    processor = test_data_processor()
    
    # 测试连续预测
    logger.info("测试连续预测...")
    test_metrics_list = [
        {
            'packets_per_sec': 1200,
            'bytes_per_sec': 1200000,
            'active_connections': 120,
            'dropped_packets': 5,
            'encryption_hits': 120,
            'decryption_hits': 120,
            'cpu_usage': 55.0,
            'memory_usage': 65.0,
            'error_count': 3
        },
        {
            'packets_per_sec': 8000,  # 异常
            'bytes_per_sec': 8000000,
            'active_connections': 800,
            'dropped_packets': 100,
            'encryption_hits': 800,
            'decryption_hits': 800,
            'cpu_usage': 95.0,
            'memory_usage': 98.0,
            'error_count': 25
        },
        {
            'packets_per_sec': 1500,  # 正常
            'bytes_per_sec': 1500000,
            'active_connections': 150,
            'dropped_packets': 8,
            'encryption_hits': 150,
            'decryption_hits': 150,
            'cpu_usage': 60.0,
            'memory_usage': 70.0,
            'error_count': 5
        }
    ]
    
    for i, metrics in enumerate(test_metrics_list):
        logger.info(f"预测 {i+1}:")
        result = detector.detect_anomaly(metrics)
        logger.info(f"  风险评分: {result.risk_score:.2f}")
        logger.info(f"  异常: {result.is_anomaly}")
        logger.info(f"  类型: {result.anomaly_type}")
    
    # 获取预测历史
    history = detector.get_prediction_history()
    logger.info(f"预测历史记录数: {len(history)}")
    
    return True

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("AI模型测试脚本")
    logger.info("=" * 60)
    
    # 创建必要的目录
    Path("models").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    try:
        # 运行所有测试
        test_integration()
        
        logger.info("=" * 60)
        logger.info("所有测试通过!")
        logger.info("=" * 60)
        
        # 生成测试报告
        report = {
            'test_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'PASSED',
            'tests': [
                '模型训练测试',
                'AI检测器测试',
                '数据处理器测试',
                '集成功能测试'
            ],
            'model_path': 'models/test_model.pth',
            'next_steps': [
                '1. 使用更多数据训练模型',
                '2. 调整模型参数优化性能',
                '3. 集成到主应用程序',
                '4. 部署到生产环境'
            ]
        }
        
        with open('test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("测试报告已保存到: test_report.json")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 