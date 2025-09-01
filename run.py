#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本
AI 驱动的 DPU 实时网络风险预警与自动防御系统
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """检查依赖"""
    required_packages = ['flask', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def start_system():
    """启动系统"""
    print("=" * 60)
    print("AI 驱动的 DPU 实时网络风险预警与自动防御系统")
    print("NVIDIA DPU 黑客松竞赛项目 - 简易版")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    print("\n✅ 依赖检查通过")
    print("🚀 启动系统...")
    
    try:
        # 启动Flask应用
        from app import app
        print("🌐 系统已启动，访问地址: http://localhost:5002")
        print("📊 实时仪表板已就绪")
        print("\n控制说明:")
        print("  - 点击 '启动模拟' 开始数据模拟")
        print("  - 点击 '触发DDoS' 模拟DDoS攻击")
        print("  - 点击 '触发资源耗尽' 模拟资源异常")
        print("  - 观察风险评分和自动防御响应")
        print("\n按 Ctrl+C 停止系统")
        
        app.run(host='0.0.0.0', port=5002, debug=False)
        
    except KeyboardInterrupt:
        print("\n\n🛑 系统已停止")
        return True
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("AI 驱动的 DPU 实时网络风险预警与自动防御系统")
        print("\n使用方法:")
        print("  python run.py          # 启动系统")
        print("  python run.py --help   # 显示帮助")
        print("\n系统功能:")
        print("  - 模拟 DPU Telemetry 数据采集")
        print("  - AI 异常检测和风险评分")
        print("  - 自动防御规则下发")
        print("  - 实时可视化监控")
        return
    
    start_system()

if __name__ == '__main__':
    main() 