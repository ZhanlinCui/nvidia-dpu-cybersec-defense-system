#!/usr/bin/env python3
"""
测试关闭防御功能
"""

from telemetry_simulator import TelemetrySimulator
from anomaly_detector import AnomalyDetector
from defense_controller import DefenseController
import time

def test_disable_defense():
    print("=" * 60)
    print("测试关闭防御功能")
    print("=" * 60)
    
    # 初始化组件
    simulator = TelemetrySimulator()
    detector = AnomalyDetector()
    controller = DefenseController(simulator=simulator)
    
    # 设置相互引用
    simulator.set_defense_controller(controller)
    
    print("1. 初始状态")
    print("-" * 40)
    print(f"防御状态: {'已激活' if controller.defense_active else '未激活'}")
    print()
    
    print("2. 触发DDoS并激活防御")
    print("-" * 40)
    simulator.trigger_anomaly("ddos")
    time.sleep(2)
    
    metrics = simulator.get_metrics()
    result = detector.detect_anomaly(metrics, defense_controller=controller)
    controller.trigger_defense(result['risk_score'], result['anomaly_type'])
    
    print(f"防御状态: {'已激活' if controller.defense_active else '未激活'}")
    print(f"风险评分: {result['risk_score']:.1f}")
    print()
    
    print("3. 关闭防御")
    print("-" * 40)
    controller.disable_defense()
    print(f"防御状态: {'已激活' if controller.defense_active else '未激活'}")
    print()
    
    print("4. 再次触发DDoS")
    print("-" * 40)
    simulator.trigger_anomaly("ddos")
    time.sleep(2)
    
    metrics = simulator.get_metrics()
    result = detector.detect_anomaly(metrics, defense_controller=controller)
    print(f"风险评分: {result['risk_score']:.1f}")
    print(f"异常模式: {'是' if simulator.anomaly_mode else '否'}")
    print()
    
    print("测试完成！")
    print("期望结果：")
    print("- 防御激活后，关闭防御应该重置状态")
    print("- 关闭防御后，新的异常应该能够正常检测")

if __name__ == "__main__":
    test_disable_defense() 