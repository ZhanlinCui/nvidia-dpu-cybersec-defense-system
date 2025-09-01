#!/usr/bin/env python3
"""
系统测试脚本
"""

from telemetry_simulator import TelemetrySimulator
from anomaly_detector import AnomalyDetector
from defense_controller import DefenseController
import time

def test_system():
    print("=" * 50)
    print("系统组件测试")
    print("=" * 50)
    
    # 初始化组件
    print("1. 初始化组件...")
    simulator = TelemetrySimulator()
    detector = AnomalyDetector()
    controller = DefenseController()
    print("✅ 组件初始化完成")
    
    # 测试正常数据
    print("\n2. 测试正常数据...")
    normal_metrics = simulator.get_metrics()
    print(f"正常指标: {normal_metrics}")
    
    normal_result = detector.detect_anomaly(normal_metrics)
    print(f"正常检测结果: 风险评分={normal_result['risk_score']:.1f}, 异常={normal_result['is_anomaly']}")
    
    # 测试DDoS异常
    print("\n3. 测试DDoS异常...")
    simulator.trigger_anomaly("ddos")
    
    for i in range(3):
        time.sleep(1)
        ddos_metrics = simulator.get_metrics()
        ddos_result = detector.detect_anomaly(ddos_metrics)
        print(f"DDoS检测结果 {i+1}: 风险评分={ddos_result['risk_score']:.1f}, 异常={ddos_result['is_anomaly']}, 类型={ddos_result['anomaly_type']}")
        
        if ddos_result['is_anomaly']:
            controller.trigger_defense(ddos_result['risk_score'])
            print(f"✅ 防御已触发，状态: {controller.get_status()}")
    
    # 测试资源耗尽异常
    print("\n4. 测试资源耗尽异常...")
    simulator.trigger_anomaly("resource_exhaustion")
    
    for i in range(3):
        time.sleep(1)
        resource_metrics = simulator.get_metrics()
        resource_result = detector.detect_anomaly(resource_metrics)
        print(f"资源耗尽检测结果 {i+1}: 风险评分={resource_result['risk_score']:.1f}, 异常={resource_result['is_anomaly']}, 类型={resource_result['anomaly_type']}")
        
        if resource_result['is_anomaly']:
            controller.trigger_defense(resource_result['risk_score'])
            print(f"✅ 防御已触发，状态: {controller.get_status()}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_system() 