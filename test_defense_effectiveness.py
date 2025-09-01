#!/usr/bin/env python3
"""
防御效果测试脚本
演示不同的防御效果百分比
"""

from defense_controller import DefenseController
import time

def test_defense_effectiveness():
    print("=" * 60)
    print("防御效果测试")
    print("=" * 60)
    
    # 测试场景1：高效果防御
    print("\n1. 高效果防御测试 (90-100%)")
    controller1 = DefenseController()
    
    # 多次成功触发
    for i in range(5):
        success = controller1.trigger_defense(85.0, "ddos_attack")
        print(f"  触发 {i+1}: {'成功' if success else '失败'}")
        time.sleep(0.1)
    
    status1 = controller1.get_status()
    effectiveness1 = status1['stats']['successful_defenses'] / status1['stats']['total_triggers'] * 100
    print(f"  防御效果: {effectiveness1:.1f}%")
    
    # 测试场景2：中等效果防御
    print("\n2. 中等效果防御测试 (60-80%)")
    controller2 = DefenseController()
    
    # 部分成功，部分失败
    for i in range(6):
        if i < 4:  # 前4次成功
            success = controller2.trigger_defense(75.0, "resource_exhaustion")
        else:  # 后2次失败（模拟）
            controller2.defense_stats['total_triggers'] += 1
            controller2.defense_stats['failed_defenses'] += 1
            success = False
        print(f"  触发 {i+1}: {'成功' if success else '失败'}")
        time.sleep(0.1)
    
    status2 = controller2.get_status()
    effectiveness2 = status2['stats']['successful_defenses'] / status2['stats']['total_triggers'] * 100
    print(f"  防御效果: {effectiveness2:.1f}%")
    
    # 测试场景3：低效果防御
    print("\n3. 低效果防御测试 (30-50%)")
    controller3 = DefenseController()
    
    # 大部分失败
    for i in range(8):
        if i < 3:  # 前3次成功
            success = controller3.trigger_defense(65.0, "packet_loss")
        else:  # 后5次失败
            controller3.defense_stats['total_triggers'] += 1
            controller3.defense_stats['failed_defenses'] += 1
            success = False
        print(f"  触发 {i+1}: {'成功' if success else '失败'}")
        time.sleep(0.1)
    
    status3 = controller3.get_status()
    effectiveness3 = status3['stats']['successful_defenses'] / status3['stats']['total_triggers'] * 100
    print(f"  防御效果: {effectiveness3:.1f}%")
    
    # 总结
    print("\n" + "=" * 60)
    print("防御效果总结")
    print("=" * 60)
    print(f"高效果防御: {effectiveness1:.1f}% - 系统运行良好")
    print(f"中等效果防御: {effectiveness2:.1f}% - 需要关注")
    print(f"低效果防御: {effectiveness3:.1f}% - 需要优化")
    
    # 建议
    print("\n建议:")
    if effectiveness1 >= 90:
        print("✅ 高效果防御 - 继续保持当前配置")
    elif effectiveness2 >= 70:
        print("⚠️  中等效果防御 - 考虑优化防御策略")
    else:
        print("❌ 低效果防御 - 需要紧急检查和修复")

if __name__ == "__main__":
    test_defense_effectiveness() 