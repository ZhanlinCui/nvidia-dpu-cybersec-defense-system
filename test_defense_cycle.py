#!/usr/bin/env python3
"""
测试防御循环功能
验证：DDoS -> 防御 -> 再次DDoS 的完整流程
"""

from telemetry_simulator import TelemetrySimulator
from anomaly_detector import AnomalyDetector
from defense_controller import DefenseController
import time

def test_defense_cycle():
    print("=" * 60)
    print("测试防御循环功能")
    print("=" * 60)
    
    # 初始化组件
    simulator = TelemetrySimulator()
    detector = AnomalyDetector()
    controller = DefenseController(simulator=simulator)
    
    # 设置相互引用
    simulator.set_defense_controller(controller)
    
    print("1. 初始状态检查")
    print("-" * 40)
    metrics = simulator.get_metrics()
    result = detector.detect_anomaly(metrics, defense_controller=controller)
    print(f"风险评分: {result['risk_score']:.1f}")
    print(f"防御状态: {'已激活' if controller.defense_active else '未激活'}")
    print(f"异常模式: {'是' if simulator.anomaly_mode else '否'}")
    print()
    
    print("2. 第一次触发DDoS")
    print("-" * 40)
    simulator.trigger_anomaly("ddos")
    time.sleep(2)  # 等待异常生效
    
    metrics = simulator.get_metrics()
    result = detector.detect_anomaly(metrics, defense_controller=controller)
    print(f"风险评分: {result['risk_score']:.1f}")
    print(f"异常类型: {result['anomaly_type']}")
    print(f"异常模式: {'是' if simulator.anomaly_mode else '否'}")
    print()
    
    print("3. 触发防御")
    print("-" * 40)
    controller.trigger_defense(result['risk_score'], result['anomaly_type'])
    time.sleep(1)
    
    metrics = simulator.get_metrics()
    result = detector.detect_anomaly(metrics, defense_controller=controller)
    print(f"风险评分: {result['risk_score']:.1f}")
    print(f"防御状态: {'已激活' if controller.defense_active else '未激活'}")
    print(f"异常模式: {'是' if simulator.anomaly_mode else '否'}")
    print()
    
    print("4. 第二次触发DDoS")
    print("-" * 40)
    simulator.trigger_anomaly("ddos")
    time.sleep(2)  # 等待异常生效
    
    metrics = simulator.get_metrics()
    result = detector.detect_anomaly(metrics, defense_controller=controller)
    print(f"风险评分: {result['risk_score']:.1f}")
    print(f"异常类型: {result['anomaly_type']}")
    print(f"防御状态: {'已激活' if controller.defense_active else '未激活'}")
    print(f"异常模式: {'是' if simulator.anomaly_mode else '否'}")
    print()
    
    print("5. 再次触发防御")
    print("-" * 40)
    controller.trigger_defense(result['risk_score'], result['anomaly_type'])
    time.sleep(1)
    
    metrics = simulator.get_metrics()
    result = detector.detect_anomaly(metrics, defense_controller=controller)
    print(f"风险评分: {result['risk_score']:.1f}")
    print(f"防御状态: {'已激活' if controller.defense_active else '未激活'}")
    print(f"异常模式: {'是' if simulator.anomaly_mode else '否'}")
    print()
    
    print("测试完成！")
    print("期望结果：")
    print("- 每次触发DDoS后，风险评分应该升高")
    print("- 每次触发防御后，风险评分应该降低")
    print("- 异常模式应该能够重新激活")

if __name__ == "__main__":
    test_defense_cycle() 