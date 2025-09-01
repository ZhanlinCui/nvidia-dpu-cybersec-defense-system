#!/usr/bin/env python3
"""
问题监控和状态检查功能展示
"""

from telemetry_simulator import TelemetrySimulator
from anomaly_detector import AnomalyDetector
from defense_controller import DefenseController
import time
import json

def show_problem_monitoring():
    print("=" * 70)
    print("问题监控和状态检查功能展示")
    print("=" * 70)
    
    # 初始化组件
    simulator = TelemetrySimulator()
    detector = AnomalyDetector()
    controller = DefenseController(simulator=simulator)
    
    print("1. 系统健康度检查")
    print("-" * 50)
    
    def check_system_health():
        """检查系统健康度"""
        metrics = simulator.get_metrics()
        result = detector.detect_anomaly(metrics, defense_controller=controller)
        
        health_issues = []
        
        # 检查网络指标
        if metrics['packets_per_sec'] > 5000:
            health_issues.append(f"⚠️  网络流量异常: {metrics['packets_per_sec']} PPS")
        
        if metrics['active_connections'] > 500:
            health_issues.append(f"⚠️  连接数异常: {metrics['active_connections']} 连接")
        
        if metrics['dropped_packets'] > 20:
            health_issues.append(f"❌ 丢包严重: {metrics['dropped_packets']} 包")
        
        if metrics['cpu_usage'] > 80:
            health_issues.append(f"🔥 CPU使用率过高: {metrics['cpu_usage']:.1f}%")
        
        if metrics['memory_usage'] > 85:
            health_issues.append(f"🔥 内存使用率过高: {metrics['memory_usage']:.1f}%")
        
        if metrics['error_count'] > 10:
            health_issues.append(f"❌ 错误计数异常: {metrics['error_count']} 个")
        
        # 检查异常检测
        if result['is_anomaly']:
            health_issues.append(f"🚨 检测到异常: {result['anomaly_type']}")
        
        # 检查防御状态
        status = controller.get_status()
        if status['active']:
            if status['active_rules_count'] == 0:
                health_issues.append("⚠️  防御已激活但无活跃规则")
            
            if status['stats']['total_triggers'] > 0:
                effectiveness = status['stats']['successful_defenses'] / status['stats']['total_triggers']
                if effectiveness < 0.7:
                    health_issues.append(f"❌ 防御效果较差: {effectiveness*100:.1f}%")
        
        return health_issues, metrics, result, status
    
    # 正常状态检查
    print("正常状态检查:")
    issues, metrics, result, status = check_system_health()
    
    if not issues:
        print("✅ 系统运行正常")
    else:
        for issue in issues:
            print(f"  {issue}")
    
    print(f"  风险评分: {result['risk_score']:.1f}")
    print(f"  防御状态: {'已激活' if status['active'] else '未激活'}")
    print()
    
    print("2. 触发DDoS攻击并监控问题")
    print("-" * 50)
    
    # 触发攻击
    simulator.trigger_anomaly("ddos")
    print("🚨 DDoS攻击已触发！")
    print()
    
    # 监控攻击过程中的问题
    for i in range(3):
        print(f"攻击后 {i+1}秒 问题检查:")
        issues, metrics, result, status = check_system_health()
        
        if issues:
            print("发现的问题:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  ✅ 暂无问题")
        
        print(f"  风险评分: {result['risk_score']:.1f}")
        print(f"  异常类型: {result['anomaly_type']}")
        
        if controller.mode == "auto" and result['is_anomaly']:
            controller.trigger_defense(result['risk_score'], result['anomaly_type'])
        
        print()
        time.sleep(1)
    
    # 新增：切换为手动模式并演示
    print("切换为手动防御模式并再次触发DDoS...")
    controller.set_mode("manual")
    simulator.trigger_anomaly("ddos")
    print("🚨 DDoS攻击已触发！（手动模式）")
    print()
    for i in range(3):
        print(f"手动模式攻击后 {i+1}秒 问题检查:")
        issues, metrics, result, status = check_system_health()
        if issues:
            print("发现的问题:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  ✅ 暂无问题")
        print(f"  风险评分: {result['risk_score']:.1f}")
        print(f"  异常类型: {result['anomaly_type']}")
        if i == 1 and result['is_anomaly']:
            print("手动触发防御！")
            controller.manual_trigger(result['risk_score'], result['anomaly_type'])
        print()
        time.sleep(1)
    
    print("3. 防御规则状态检查")
    print("-" * 50)
    
    final_status = controller.get_status()
    
    print("📋 防御规则状态:")
    print(f"  总规则数: {final_status['total_rules']}")
    print(f"  活跃规则数: {final_status['active_rules_count']}")
    print(f"  过期规则数: {final_status['total_rules'] - final_status['active_rules_count']}")
    
    if final_status['recent_rules']:
        print("\n最近应用的规则:")
        for i, rule in enumerate(final_status['recent_rules'][-3:], 1):
            print(f"  规则 {i}:")
            print(f"    动作: {rule['strategy']['actions']}")
            print(f"    优先级: {rule['strategy']['priority']}")
            print(f"    成功: {'✅' if rule['success'] else '❌'}")
            print(f"    时间: {time.strftime('%H:%M:%S', time.localtime(rule['timestamp']))}")
    
    print("\n4. 系统性能指标监控")
    print("-" * 50)
    
    current_metrics = simulator.get_metrics()
    
    print("📊 当前性能指标:")
    print(f"  网络性能:")
    print(f"    数据包/秒: {current_metrics['packets_per_sec']} PPS")
    print(f"    字节/秒: {current_metrics['bytes_per_sec']} B/s")
    print(f"    活跃连接: {current_metrics['active_connections']}")
    print(f"    丢包数: {current_metrics['dropped_packets']}")
    
    print(f"  系统资源:")
    print(f"    CPU使用率: {current_metrics['cpu_usage']:.1f}%")
    print(f"    内存使用率: {current_metrics['memory_usage']:.1f}%")
    print(f"    错误计数: {current_metrics['error_count']}")
    
    print(f"  安全指标:")
    print(f"    加密命中: {current_metrics['encryption_hits']}")
    print(f"    解密命中: {current_metrics['decryption_hits']}")
    
    print("\n5. 异常检测统计")
    print("-" * 50)
    
    detector_stats = detector.get_statistics()
    print(f"  总检测次数: {detector_stats['total_detections']}")
    print(f"  当前阈值: {detector_stats['current_thresholds']}")
    print(f"  历史数据量: {detector_stats['history_size']}")
    
    print("\n6. 防御效果评估")
    print("-" * 50)
    
    if final_status['stats']['total_triggers'] > 0:
        effectiveness = final_status['stats']['successful_defenses'] / final_status['stats']['total_triggers'] * 100
        
        print(f"  防御成功率: {effectiveness:.1f}%")
        print(f"  总触发次数: {final_status['stats']['total_triggers']}")
        print(f"  成功次数: {final_status['stats']['successful_defenses']}")
        print(f"  失败次数: {final_status['stats']['failed_defenses']}")
        
        if effectiveness >= 90:
            print("  🟢 防御效果: 优秀")
        elif effectiveness >= 70:
            print("  🟡 防御效果: 良好")
        elif effectiveness >= 50:
            print("  🟠 防御效果: 一般")
        else:
            print("  🔴 防御效果: 较差")
    
    print("\n7. 系统建议")
    print("-" * 50)
    
    # 生成系统建议
    suggestions = []
    
    if current_metrics['cpu_usage'] > 70:
        suggestions.append("建议优化CPU密集型任务")
    
    if current_metrics['memory_usage'] > 80:
        suggestions.append("建议增加内存或优化内存使用")
    
    if current_metrics['dropped_packets'] > 10:
        suggestions.append("建议检查网络配置和带宽")
    
    if final_status['active_rules_count'] > 10:
        suggestions.append("建议清理过期的防御规则")
    
    if suggestions:
        print("系统建议:")
        for suggestion in suggestions:
            print(f"  💡 {suggestion}")
    else:
        print("  ✅ 系统运行良好，无需特别建议")

if __name__ == "__main__":
    show_problem_monitoring() 