#!/usr/bin/env python3
"""
防御控制器 (简化版)
模拟 DPU Flow 规则下发和自动防御
"""

import time
import json
from typing import Dict, Any, List
from collections import deque

class DefenseController:
    """防御控制器"""
    
    def __init__(self, simulator=None):
        # 防御规则
        self.defense_rules = []
        self.max_rules = 100
        
        # 防御策略
        self.defense_strategies = {
            'ddos_attack': {
                'actions': ['rate_limit', 'connection_limit', 'drop_suspicious'],
                'priority': 'high',
                'duration': 300  # 5分钟
            },
            'resource_exhaustion': {
                'actions': ['cpu_throttle', 'memory_limit', 'error_monitoring'],
                'priority': 'medium',
                'duration': 180  # 3分钟
            },
            'packet_loss': {
                'actions': ['retry_mechanism', 'buffer_optimization'],
                'priority': 'low',
                'duration': 120  # 2分钟
            },
            'suspicious_behavior': {
                'actions': ['traffic_analysis', 'encryption_monitoring'],
                'priority': 'medium',
                'duration': 240  # 4分钟
            }
        }
        
        # 防御状态
        self.defense_active = False
        self.last_trigger_time = 0
        self.current_strategy = None
        
        # 统计信息
        self.defense_stats = {
            'total_triggers': 0,
            'successful_defenses': 0,
            'failed_defenses': 0,
            'last_defense_time': 0
        }
        
        # 规则历史
        self.rule_history = deque(maxlen=50)
        
        # 新增：防御模式，auto/手动
        self.mode = "auto"  # "auto" 或 "manual"
        
        # 新增：与模拟器联动
        self.simulator = simulator
    
    def set_mode(self, mode):
        assert mode in ("auto", "manual")
        self.mode = mode
        print(f"防御模式已切换为: {mode}")
    
    def trigger_defense(self, risk_score: float, anomaly_type: str = None):
        """触发防御机制"""
        current_time = time.time()
        
        # 确定防御策略
        if anomaly_type and anomaly_type in self.defense_strategies:
            strategy = self.defense_strategies[anomaly_type]
        else:
            # 基于风险评分选择策略
            if risk_score > 90:
                strategy = self.defense_strategies['ddos_attack']
            elif risk_score > 80:
                strategy = self.defense_strategies['resource_exhaustion']
            elif risk_score > 70:
                strategy = self.defense_strategies['packet_loss']
            else:
                strategy = self.defense_strategies['suspicious_behavior']
        
        # 生成防御规则
        rules = self._generate_defense_rules(strategy, risk_score)
        
        # 应用规则
        success = self._apply_defense_rules(rules)
        
        # 更新状态
        self.defense_active = True
        self.last_trigger_time = current_time
        self.current_strategy = strategy
        
        # 更新统计信息
        self.defense_stats['total_triggers'] += 1
        self.defense_stats['last_defense_time'] = current_time
        
        if success:
            self.defense_stats['successful_defenses'] += 1
        else:
            self.defense_stats['failed_defenses'] += 1
        
        # 记录规则历史
        rule_record = {
            'timestamp': current_time,
            'risk_score': risk_score,
            'anomaly_type': anomaly_type,
            'strategy': strategy,
            'rules': rules,
            'success': success
        }
        self.rule_history.append(rule_record)
        
        print(f"防御已触发: 风险评分={risk_score:.1f}, 策略={strategy['actions']}")
        
        # 新增：防御激活后关闭模拟器异常
        if self.simulator is not None:
            self.simulator.anomaly_mode = False
            self.simulator.anomaly_type = "normal"
            print("防御激活，模拟器异常已关闭，系统恢复正常")
        
        return success
    
    def _generate_defense_rules(self, strategy: Dict[str, Any], risk_score: float) -> List[Dict[str, Any]]:
        """生成防御规则"""
        rules = []
        
        for action in strategy['actions']:
            rule = {
                'id': f"rule_{int(time.time())}_{len(rules)}",
                'action': action,
                'priority': strategy['priority'],
                'created_time': time.time(),
                'expires_time': time.time() + strategy['duration'],
                'conditions': self._get_action_conditions(action, risk_score),
                'parameters': self._get_action_parameters(action, risk_score)
            }
            rules.append(rule)
        
        return rules
    
    def _get_action_conditions(self, action: str, risk_score: float) -> Dict[str, Any]:
        """获取动作条件"""
        conditions = {
            'rate_limit': {
                'packets_per_sec_threshold': 1000 + risk_score * 10,
                'bytes_per_sec_threshold': 1000000 + risk_score * 10000
            },
            'connection_limit': {
                'max_connections': max(50, 200 - risk_score * 2),
                'connection_timeout': 30
            },
            'drop_suspicious': {
                'suspicious_patterns': ['high_frequency', 'large_packets', 'encrypted_traffic'],
                'drop_probability': min(0.8, risk_score / 100)
            },
            'cpu_throttle': {
                'max_cpu_usage': max(30, 80 - risk_score * 0.5),
                'throttle_duration': 60
            },
            'memory_limit': {
                'max_memory_usage': max(40, 70 - risk_score * 0.3),
                'cleanup_interval': 30
            },
            'error_monitoring': {
                'error_threshold': max(5, 20 - risk_score * 0.2),
                'monitoring_interval': 10
            },
            'retry_mechanism': {
                'max_retries': 3,
                'retry_delay': 1
            },
            'buffer_optimization': {
                'buffer_size': max(1024, 8192 - risk_score * 50),
                'optimization_interval': 15
            },
            'traffic_analysis': {
                'analysis_depth': 'deep' if risk_score > 80 else 'normal',
                'sampling_rate': max(0.1, 1.0 - risk_score / 100)
            },
            'encryption_monitoring': {
                'encryption_ratio_threshold': 0.7,
                'monitoring_interval': 5
            }
        }
        
        return conditions.get(action, {})
    
    def _get_action_parameters(self, action: str, risk_score: float) -> Dict[str, Any]:
        """获取动作参数"""
        parameters = {
            'rate_limit': {
                'limit_type': 'packet_rate',
                'limit_value': max(100, 1000 - risk_score * 5)
            },
            'connection_limit': {
                'limit_type': 'connection_count',
                'limit_value': max(10, 100 - risk_score)
            },
            'drop_suspicious': {
                'drop_type': 'selective',
                'drop_rate': min(0.9, risk_score / 100)
            },
            'cpu_throttle': {
                'throttle_type': 'percentage',
                'throttle_value': min(50, risk_score * 0.5)
            },
            'memory_limit': {
                'limit_type': 'percentage',
                'limit_value': min(30, risk_score * 0.3)
            },
            'error_monitoring': {
                'monitoring_type': 'real_time',
                'alert_threshold': max(1, 10 - risk_score * 0.1)
            },
            'retry_mechanism': {
                'retry_type': 'exponential_backoff',
                'max_delay': 5
            },
            'buffer_optimization': {
                'optimization_type': 'dynamic',
                'target_efficiency': 0.8
            },
            'traffic_analysis': {
                'analysis_type': 'behavioral',
                'learning_rate': 0.1
            },
            'encryption_monitoring': {
                'monitoring_type': 'ratio_based',
                'alert_threshold': 0.8
            }
        }
        
        return parameters.get(action, {})
    
    def _apply_defense_rules(self, rules: List[Dict[str, Any]]) -> bool:
        """应用防御规则"""
        try:
            # 模拟规则下发到 DPU
            for rule in rules:
                # 添加到规则列表
                self.defense_rules.append(rule)
                
                # 保持规则数量限制
                if len(self.defense_rules) > self.max_rules:
                    self.defense_rules.pop(0)
                
                print(f"规则已下发: {rule['action']} (优先级: {rule['priority']})")
            
            return True
            
        except Exception as e:
            print(f"规则下发失败: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取防御状态"""
        # 清理过期规则
        current_time = time.time()
        active_rules = [rule for rule in self.defense_rules if rule['expires_time'] > current_time]
        self.defense_rules = active_rules
        
        return {
            'active': self.defense_active,
            'current_strategy': self.current_strategy,
            'active_rules_count': len(active_rules),
            'total_rules': len(self.defense_rules),
            'last_trigger_time': self.last_trigger_time,
            'stats': self.defense_stats,
            'recent_rules': list(self.rule_history)[-5:] if self.rule_history else []
        }
    
    def clear_rules(self):
        """清除所有规则"""
        self.defense_rules.clear()
        self.defense_active = False
        self.current_strategy = None
        print("所有防御规则已清除")
    
    def get_rule_by_id(self, rule_id: str) -> Dict[str, Any]:
        """根据ID获取规则"""
        for rule in self.defense_rules:
            if rule['id'] == rule_id:
                return rule
        return {}
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """更新规则"""
        for rule in self.defense_rules:
            if rule['id'] == rule_id:
                rule.update(updates)
                print(f"规则已更新: {rule_id}")
                return True
        return False
    
    def get_defense_summary(self) -> Dict[str, Any]:
        """获取防御摘要"""
        current_time = time.time()
        active_rules = [rule for rule in self.defense_rules if rule['expires_time'] > current_time]
        
        # 按动作类型统计
        action_stats = {}
        for rule in active_rules:
            action = rule['action']
            if action not in action_stats:
                action_stats[action] = 0
            action_stats[action] += 1
        
        return {
            'total_active_rules': len(active_rules),
            'action_distribution': action_stats,
            'defense_effectiveness': self._calculate_effectiveness(),
            'recent_activity': len([r for r in self.rule_history if current_time - r['timestamp'] < 300])
        }
    
    def _calculate_effectiveness(self) -> float:
        """计算防御效果"""
        if self.defense_stats['total_triggers'] == 0:
            return 0.0
        
        success_rate = self.defense_stats['successful_defenses'] / self.defense_stats['total_triggers']
        
        # 考虑最近的活动
        recent_triggers = 0
        current_time = time.time()
        for record in self.rule_history:
            if current_time - record['timestamp'] < 600:  # 最近10分钟
                recent_triggers += 1
        
        # 如果最近有活动，增加效果评分
        if recent_triggers > 0:
            effectiveness = success_rate * 0.7 + min(1.0, recent_triggers / 10) * 0.3
        else:
            effectiveness = success_rate
        
        return min(1.0, effectiveness)

    # 新增：手动触发防御的接口
    def manual_trigger(self, risk_score: float, anomaly_type: str = None):
        if self.mode == "manual":
            return self.trigger_defense(risk_score, anomaly_type)
        else:
            print("当前为自动模式，手动触发无效")
            return False

    # 新增：重置防御状态，允许新的异常检测
    def reset_defense_state(self):
        """重置防御状态，允许新的异常检测"""
        self.defense_active = False
        self.current_strategy = None
        self.last_trigger_time = 0
        print("防御状态已重置，允许新的异常检测")

    # 新增：通知新的异常触发
    def notify_new_anomaly(self, anomaly_type: str):
        """通知有新的异常触发，重置防御状态"""
        print(f"检测到新的异常: {anomaly_type}，重置防御状态")
        self.reset_defense_state()

    # 新增：关闭防御
    def disable_defense(self):
        """关闭防御系统"""
        self.defense_active = False
        self.current_strategy = None
        self.last_trigger_time = 0
        print("防御系统已关闭")
        return True

    # 新增：获取防御状态描述
    def get_defense_status_description(self):
        """获取防御状态描述"""
        if self.defense_active:
            if self.current_strategy:
                actions = ', '.join(self.current_strategy['actions'])
                return f"已激活 - {actions}"
            else:
                return "已激活 - 无策略"
        else:
            return "未激活"

# 测试代码
if __name__ == "__main__":
    controller = DefenseController()
    
    # 测试防御触发
    print("测试防御控制器...")
    
    # 触发DDoS防御
    success = controller.trigger_defense(85.0, "ddos_attack")
    print(f"DDoS防御触发结果: {success}")
    
    # 获取状态
    status = controller.get_status()
    print(f"防御状态: {status}")
    
    # 触发资源耗尽防御
    success = controller.trigger_defense(75.0, "resource_exhaustion")
    print(f"资源耗尽防御触发结果: {success}")
    
    # 获取摘要
    summary = controller.get_defense_summary()
    print(f"防御摘要: {summary}") 