#!/usr/bin/env python3
"""
生成预测演示数据
"""

import time
import random
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telemetry_simulator import TelemetrySimulator
from integrate_ai_detector import HybridAnomalyDetector

def main():
    """主函数"""
    print("🚀 开始生成预测演示数据...")
    print("=" * 50)
    
    # 初始化模拟器和检测器
    simulator = TelemetrySimulator()
    hybrid_detector = HybridAnomalyDetector()
    
    # 生成正常数据（前20个数据点）
    print("📊 生成正常网络数据...")
    for i in range(20):
        metrics = simulator.get_metrics()
        result = hybrid_detector.detect_anomaly(metrics)
        print(f"✓ 数据点 {i+1}: CPU={metrics['cpu_usage']:.1f}%, 风险评分={result['risk_score']:.1f}")
        time.sleep(0.5)
    
    # 生成异常数据（接下来10个数据点）
    print("\n⚠️  生成异常网络数据...")
    simulator.trigger_anomaly('ddos_attack')
    for i in range(10):
        metrics = simulator.get_metrics()
        result = hybrid_detector.detect_anomaly(metrics)
        print(f"⚠️  异常数据 {i+1}: CPU={metrics['cpu_usage']:.1f}%, 风险评分={result['risk_score']:.1f}")
        time.sleep(0.5)
    
    # 生成恢复数据（最后10个数据点）
    print("\n🔄 生成网络恢复数据...")
    simulator.reset_anomaly()
    for i in range(10):
        metrics = simulator.get_metrics()
        result = hybrid_detector.detect_anomaly(metrics)
        print(f"🔄 恢复数据 {i+1}: CPU={metrics['cpu_usage']:.1f}%, 风险评分={result['risk_score']:.1f}")
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("✅ 演示数据生成完成！")
    print("🌐 请访问 http://localhost:5002 查看预测性分析结果")
    print("📈 预测功能包括：")
    print("   • 攻击概率预测图表")
    print("   • 风险热力图")
    print("   • 预测洞察分析")
    print("   • 风险时间线")
    
    # 测试预测功能
    print("\n🔮 测试预测功能...")
    try:
        prediction = hybrid_detector.get_prediction_data(24)
        if 'error' not in prediction:
            print("✅ 预测功能正常")
            print(f"   预测置信度: {prediction.get('confidence', 0):.2f}")
            print(f"   数据点数量: {prediction.get('data_points_used', 0)}")
        else:
            print(f"⚠️  预测功能: {prediction['error']}")
    except Exception as e:
        print(f"❌ 预测功能错误: {e}")

if __name__ == "__main__":
    main() 