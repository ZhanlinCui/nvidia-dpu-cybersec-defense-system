#!/usr/bin/env python3
"""
DDoS攻击防御效果观察脚本
"""

from telemetry_simulator import TelemetrySimulator
from anomaly_detector import AnomalyDetector
from defense_controller import DefenseController
import time

def observe_ddos_defense():
    print("=" * 60)
    print("DDoS攻击防御效果观察")
    print("=" * 60)
    
    # 初始化组件
    simulator = TelemetrySimulator()
    detector = AnomalyDetector()
    controller = DefenseController()
    
    print("1. 正常状态观察")
    print("-" * 40)
    
    # 观察正常状态
    for i in range(3):
        metrics = simulator.get_metrics()
        result = detector.detect_anomaly(metrics)
        
        print(f"时间 {i+1}:")
        print(f"  风险评分: {result['risk_score']:.1f}")
        print(f"  是否异常: {result['is_anomaly']}")
        print(f"  异常类型: {result['anomaly_type']}")
        print(f"  防御状态: {'已激活' if controller.defense_active else '未激活'}")
        print(f"  活跃规则数: {len(controller.defense_rules)}")
        
        status = controller.get_status()
        if status['stats']['total_triggers'] > 0:
            effectiveness = status['stats']['successful_defenses'] / status['stats']['total_triggers'] * 100
            print(f"  防御效果: {effectiveness:.1f}%")
        else:
            print(f"  防御效果: 0%")
        print()
        time.sleep(1)
    
    print("2. 触发DDoS攻击")
    print("-" * 40)
    
    # 触发DDoS攻击
    simulator.trigger_anomaly("ddos")
    print("🚨 DDoS攻击已触发！")
    print()
    
    # 观察攻击和防御过程
    for i in range(5):
        metrics = simulator.get_metrics()
        result = detector.detect_anomaly(metrics)
        
        print(f"攻击后 {i+1}秒:")
        print(f"  网络指标:")
        print(f"    数据包/秒: {metrics['packets_per_sec']}")
        print(f"    活跃连接: {metrics['active_connections']}")
        print(f"    丢包数: {metrics['dropped_packets']}")
        print(f"    CPU使用率: {metrics['cpu_usage']:.1f}%")
        
        print(f"  异常检测:")
        print(f"    风险评分: {result['risk_score']:.1f}")
        print(f"    是否异常: {result['is_anomaly']}")
        print(f"    异常类型: {result['anomaly_type']}")
        
        # 如果检测到异常，触发防御
        if result['is_anomaly']:
            controller.trigger_defense(result['risk_score'], result['anomaly_type'])
        
        status = controller.get_status()
        print(f"  防御状态:")
        print(f"    防御激活: {status['active']}")
        print(f"    活跃规则数: {status['active_rules_count']}")
        print(f"    总规则数: {status['total_rules']}")
        
        if status['stats']['total_triggers'] > 0:
            effectiveness = status['stats']['successful_defenses'] / status['stats']['total_triggers'] * 100
            print(f"    防御效果: {effectiveness:.1f}%")
        
        if status['current_strategy']:
            print(f"    当前策略: {status['current_strategy']['actions']}")
            print(f"    策略优先级: {status['current_strategy']['priority']}")
        
        print()
        time.sleep(1)
    
    print("3. 防御效果总结")
    print("-" * 40)
    
    final_status = controller.get_status()
    
    print("📊 最终防御效果:")
    print(f"  总触发次数: {final_status['stats']['total_triggers']}")
    print(f"  成功防御次数: {final_status['stats']['successful_defenses']}")
    print(f"  失败防御次数: {final_status['stats']['failed_defenses']}")
    
    if final_status['stats']['total_triggers'] > 0:
        effectiveness = final_status['stats']['successful_defenses'] / final_status['stats']['total_triggers'] * 100
        print(f"  防御成功率: {effectiveness:.1f}%")
        
        if effectiveness >= 90:
            print("  🟢 防御效果: 优秀")
        elif effectiveness >= 70:
            print("  🟡 防御效果: 良好")
        elif effectiveness >= 50:
            print("  🟠 防御效果: 一般")
        else:
            print("  🔴 防御效果: 较差")
    
    print(f"  活跃防御规则: {final_status['active_rules_count']}")
    
    # 显示具体的防御规则
    if final_status['recent_rules']:
        print("\n📋 最近应用的防御规则:")
        for i, rule_record in enumerate(final_status['recent_rules'][-3:], 1):
            print(f"  规则 {i}:")
            print(f"    时间: {time.strftime('%H:%M:%S', time.localtime(rule_record['timestamp']))}")
            print(f"    风险评分: {rule_record['risk_score']:.1f}")
            print(f"    策略: {rule_record['strategy']['actions']}")
            print(f"    优先级: {rule_record['strategy']['priority']}")
            print(f"    成功: {'是' if rule_record['success'] else '否'}")

if __name__ == "__main__":
    observe_ddos_defense() 