#!/usr/bin/env python3
"""
AI模型训练脚本
用于训练和测试LSTM异常检测模型
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_engine.models.simple_lstm import AnomalyPredictor, ModelConfig, create_sample_data
from src.ai_engine.training.data_processor import DataProcessor, create_synthetic_data
from src.ai_engine.inference.ai_anomaly_detector import AIAnomalyDetector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directories():
    """创建必要的目录"""
    directories = ['models', 'data', 'logs', 'configs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")

def train_model_with_synthetic_data():
    """使用合成数据训练模型"""
    logger.info("开始使用合成数据训练模型...")
    
    # 创建模型配置
    config = ModelConfig(
        input_size=9,
        hidden_size=64,
        num_layers=2,
        sequence_length=10,
        dropout=0.2,
        learning_rate=0.001,
        batch_size=32,
        epochs=50  # 减少训练轮数以加快速度
    )
    
    # 创建预测器
    predictor = AnomalyPredictor(config)
    
    # 生成合成数据
    logger.info("生成合成训练数据...")
    train_data, train_labels = create_sample_data(2000, config.sequence_length)
    val_data, val_labels = create_sample_data(500, config.sequence_length)
    
    logger.info(f"训练数据: {len(train_data)} 样本")
    logger.info(f"验证数据: {len(val_data)} 样本")
    logger.info(f"异常样本比例: {np.sum(train_labels) / len(train_labels):.2%}")
    
    # 训练模型
    logger.info("开始训练模型...")
    history = predictor.train(train_data, train_labels, val_data, val_labels)
    
    # 保存模型
    model_path = "models/anomaly_lstm.pth"
    predictor.save_model(model_path)
    logger.info(f"模型已保存到: {model_path}")
    
    # 测试模型
    logger.info("测试模型性能...")
    test_data, test_labels = create_sample_data(100, config.sequence_length)
    predictions = predictor.predict(test_data)
    
    # 计算准确率
    predicted_labels = (predictions > 0.5).astype(int)
    accuracy = np.mean(predicted_labels == test_labels)
    logger.info(f"测试准确率: {accuracy:.4f}")
    
    return model_path, history

def train_model_with_processor():
    """使用数据处理器训练模型"""
    logger.info("开始使用数据处理器训练模型...")
    
    # 创建数据处理器
    processor = DataProcessor(sequence_length=10)
    
    # 生成合成数据
    logger.info("生成合成数据...")
    sequences, labels = create_synthetic_data(2000, 0.2)
    
    # 获取训练数据
    train_seq, train_labels, val_seq, val_labels = processor.get_training_data()
    
    if len(train_seq) == 0:
        logger.error("没有足够的训练数据")
        return None, None
    
    # 创建模型配置
    config = ModelConfig(
        input_size=9,
        hidden_size=64,
        num_layers=2,
        sequence_length=10,
        dropout=0.2,
        learning_rate=0.001,
        batch_size=32,
        epochs=50
    )
    
    # 创建预测器
    predictor = AnomalyPredictor(config)
    
    # 训练模型
    logger.info("开始训练模型...")
    history = predictor.train(train_seq, train_labels, val_seq, val_labels)
    
    # 保存模型
    model_path = "models/anomaly_lstm_processor.pth"
    predictor.save_model(model_path)
    logger.info(f"模型已保存到: {model_path}")
    
    return model_path, history

def test_ai_detector(model_path: str):
    """测试AI检测器"""
    logger.info("测试AI异常检测器...")
    
    # 创建AI检测器
    detector = AIAnomalyDetector(model_path=model_path)
    
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
    
    # 检测正常数据
    logger.info("检测正常数据...")
    normal_result = detector.detect_anomaly(normal_metrics)
    logger.info(f"正常数据检测结果: 风险评分={normal_result.risk_score:.2f}, 异常={normal_result.is_anomaly}")
    
    # 检测异常数据
    logger.info("检测异常数据...")
    anomaly_result = detector.detect_anomaly(anomaly_metrics)
    logger.info(f"异常数据检测结果: 风险评分={anomaly_result.risk_score:.2f}, 异常={anomaly_result.is_anomaly}")
    
    # 获取模型状态
    status = detector.get_model_status()
    logger.info(f"模型状态: {status}")
    
    return detector

def create_config_file():
    """创建配置文件"""
    config = {
        'model': {
            'input_size': 9,
            'hidden_size': 64,
            'num_layers': 2,
            'sequence_length': 10,
            'dropout': 0.2,
            'learning_rate': 0.001,
            'batch_size': 32,
            'epochs': 100
        },
        'detection': {
            'risk_threshold': 0.7,
            'confidence_threshold': 0.6,
            'update_interval': 1.0,
            'prediction_window': 10
        },
        'anomaly_types': {
            'ddos_attack': {'threshold': 0.8, 'weight': 1.0},
            'resource_exhaustion': {'threshold': 0.7, 'weight': 0.8},
            'packet_loss': {'threshold': 0.6, 'weight': 0.6},
            'suspicious_behavior': {'threshold': 0.5, 'weight': 0.7}
        }
    }
    
    config_path = "configs/ai_model_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"配置文件已创建: {config_path}")
    return config_path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI模型训练脚本')
    parser.add_argument('--mode', choices=['train', 'test', 'both'], default='both',
                       help='运行模式: train(训练), test(测试), both(训练+测试)')
    parser.add_argument('--model-path', type=str, default='models/anomaly_lstm.pth',
                       help='模型保存路径')
    parser.add_argument('--epochs', type=int, default=50,
                       help='训练轮数')
    parser.add_argument('--data-size', type=int, default=2000,
                       help='训练数据大小')
    
    args = parser.parse_args()
    
    # 创建目录
    create_directories()
    
    # 创建配置文件
    config_path = create_config_file()
    
    model_path = None
    detector = None
    
    if args.mode in ['train', 'both']:
        logger.info("=" * 50)
        logger.info("开始训练AI模型")
        logger.info("=" * 50)
        
        # 训练模型
        model_path, history = train_model_with_synthetic_data()
        
        if model_path:
            logger.info("模型训练完成!")
        else:
            logger.error("模型训练失败!")
            return
    
    if args.mode in ['test', 'both']:
        logger.info("=" * 50)
        logger.info("开始测试AI模型")
        logger.info("=" * 50)
        
        # 如果没有训练，使用指定路径
        if not model_path:
            model_path = args.model_path
        
        if os.path.exists(model_path):
            detector = test_ai_detector(model_path)
            logger.info("AI模型测试完成!")
        else:
            logger.error(f"模型文件不存在: {model_path}")
    
    logger.info("=" * 50)
    logger.info("AI模型训练和测试完成!")
    logger.info("=" * 50)
    
    # 保存使用说明
    usage_info = {
        'model_path': model_path,
        'config_path': config_path,
        'usage': {
            'load_model': f"detector = AIAnomalyDetector(model_path='{model_path}')",
            'detect_anomaly': "result = detector.detect_anomaly(metrics_dict)",
            'get_status': "status = detector.get_model_status()"
        }
    }
    
    with open('models/usage_info.json', 'w') as f:
        json.dump(usage_info, f, indent=2)
    
    logger.info("使用说明已保存到: models/usage_info.json")

if __name__ == "__main__":
    import numpy as np
    main() 