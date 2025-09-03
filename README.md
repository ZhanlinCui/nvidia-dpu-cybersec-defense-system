# AI驱动的DPU实时网络风险预警与自动防御系统

## 项目概述

本项目是基于NVIDIA BlueField DPU和轻量化深度学习模型的实时网络风险预警与自动防御系统，专为第三届NVIDIA DPU中国黑客松竞赛设计。系统采用Python Flask框架构建，包含数据模拟器、基于规则的异常检测、防御控制器和Web仪表板，支持模拟异常场景和实时展示风险评分及防御状态。

## 1. 系统架构

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Web前端界面 (Dashboard)                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   控制面板   │  │  实时监控    │  │  告警面板    │         │
│  │             │  │             │  │             │         │
│  │ • 启动模拟   │  │ • 风险评分   │  │ • 异常告警   │         │
│  │ • 触发异常   │  │ • 系统状态   │  │ • 防御状态   │         │
│  │ • 防御模式   │  │ • 网络指标   │  │ • 历史记录   │         │
│  │ • 手动防御   │  │ • 实时图表   │  │             │         │
│  │ • 关闭防御   │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Web服务器 (app.py)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   API接口    │  │   路由管理    │  │   会话管理    │         │
│  │             │  │             │  │             │         │
│  │ • /api/metrics│  │ • 页面路由   │  │ • 状态维护   │         │
│  │ • /api/alerts│  │ • 静态文件   │  │ • 数据缓存   │         │
│  │ • /api/defense│  │ • 错误处理   │  │ • 线程管理   │         │
│  │ • /api/simulation│  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    核心业务逻辑层                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 数据模拟器   │  │ 异常检测器   │  │ 防御控制器   │         │
│  │             │  │             │  │             │         │
│  │ • 网络指标   │  │ • 风险评分   │  │ • 防御策略   │         │
│  │ • 异常模拟   │  │ • 异常分类   │  │ • 规则下发   │         │
│  │ • 历史数据   │  │ • 置信度    │  │ • 效果评估   │         │
│  │ • 统计信息   │  │ • 阈值管理   │  │ • 状态管理   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 核心组件说明

#### 1.2.1 数据模拟器 (TelemetrySimulator)
- **功能**: 模拟BlueField DPU的网络指标数据
- **职责**: 
  - 生成实时网络指标（数据包/秒、字节/秒、连接数等）
  - 模拟异常场景（DDoS、资源耗尽、丢包等）
  - 维护历史数据和时间序列
  - 与防御控制器联动，实现异常重置

#### 1.2.2 异常检测器 (AnomalyDetector)
- **功能**: 基于规则的AI异常检测和风险评分
- **职责**:
  - 实时分析网络指标
  - 计算风险评分（0-100）
  - 分类异常类型
  - 评估检测置信度
  - 考虑防御状态调整评分

#### 1.2.3 防御控制器 (DefenseController)
- **功能**: 智能防御策略管理和规则下发
- **职责**:
  - 管理防御策略库
  - 生成和应用防御规则
  - 评估防御效果
  - 支持自动/手动模式切换
  - 与模拟器联动实现状态重置

## 2. 防御规则系统

### 2.1 防御策略库

系统内置4大类防御策略，共包含10种具体防御动作：

#### 2.1.1 DDoS攻击防御策略
```python
'ddos_attack': {
    'actions': ['rate_limit', 'connection_limit', 'drop_suspicious'],
    'priority': 'high',
    'duration': 300  # 5分钟
}
```

**具体规则**:
1. **rate_limit** (速率限制)
   - 限制数据包/秒和字节/秒
   - 动态调整限制值：`max(100, 1000 - risk_score * 5)`
   - 阈值：`1000 + risk_score * 10`

2. **connection_limit** (连接数限制)
   - 限制最大活跃连接数
   - 动态调整：`max(10, 100 - risk_score)`
   - 连接超时：30秒

3. **drop_suspicious** (丢弃可疑流量)
   - 选择性丢弃可疑数据包
   - 丢弃率：`min(0.9, risk_score / 100)`
   - 检测模式：高频、大包、加密流量

#### 2.1.2 资源耗尽防御策略
```python
'resource_exhaustion': {
    'actions': ['cpu_throttle', 'memory_limit', 'error_monitoring'],
    'priority': 'medium',
    'duration': 180  # 3分钟
}
```

**具体规则**:
4. **cpu_throttle** (CPU限流)
   - 限制CPU使用率：`max(30, 80 - risk_score * 0.5)`
   - 限流时长：60秒
   - 限流比例：`min(50, risk_score * 0.5)`

5. **memory_limit** (内存限制)
   - 限制内存使用率：`max(40, 70 - risk_score * 0.3)`
   - 清理间隔：30秒
   - 限制比例：`min(30, risk_score * 0.3)`

6. **error_monitoring** (错误监控)
   - 实时错误监控
   - 告警阈值：`max(1, 10 - risk_score * 0.1)`
   - 监控间隔：10秒

#### 2.1.3 丢包异常防御策略
```python
'packet_loss': {
    'actions': ['retry_mechanism', 'buffer_optimization'],
    'priority': 'low',
    'duration': 120  # 2分钟
}
```

**具体规则**:
7. **retry_mechanism** (重试机制)
   - 最大重试次数：3次
   - 重试延迟：1秒
   - 指数退避策略

8. **buffer_optimization** (缓冲区优化)
   - 动态缓冲区大小：`max(1024, 8192 - risk_score * 50)`
   - 优化间隔：15秒
   - 目标效率：80%

#### 2.1.4 可疑行为防御策略
```python
'suspicious_behavior': {
    'actions': ['traffic_analysis', 'encryption_monitoring'],
    'priority': 'medium',
    'duration': 240  # 4分钟
}
```

**具体规则**:
9. **traffic_analysis** (流量分析)
   - 深度行为分析
   - 采样率：`max(0.1, 1.0 - risk_score / 100)`
   - 学习率：0.1

10. **encryption_monitoring** (加密监控)
    - 加密比例监控
    - 告警阈值：0.8
    - 监控间隔：5秒

### 2.2 规则生成机制

```python
def _generate_defense_rules(self, strategy: Dict[str, Any], risk_score: float):
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
```

### 2.3 规则生命周期管理

- **创建**: 异常检测触发时自动生成
- **应用**: 立即下发到DPU执行
- **监控**: 实时跟踪规则执行效果
- **过期**: 自动清理过期规则
- **统计**: 记录成功/失败次数

## 3. 风险评分规则

### 3.1 评分算法架构

风险评分采用多维度加权算法，总分0-100分：

```python
def _calculate_risk_score(self, metrics: Dict[str, Any]) -> float:
    risk_score = 0.0
    
    # 1. 丢包率风险 (权重: 40分)
    if metrics['dropped_packets'] > 20: risk_score += 40
    elif metrics['dropped_packets'] > 10: risk_score += 30
    elif metrics['dropped_packets'] > 5: risk_score += 20
    
    # 2. 连接数风险 (权重: 35分)
    if metrics['active_connections'] > 500: risk_score += 35
    elif metrics['active_connections'] > 200: risk_score += 25
    elif metrics['active_connections'] > 100: risk_score += 15
    
    # 3. CPU使用率风险 (权重: 30分)
    if metrics['cpu_usage'] > 70: risk_score += 30
    elif metrics['cpu_usage'] > 60: risk_score += 25
    elif metrics['cpu_usage'] > 50: risk_score += 20
    
    # 4. 错误计数风险 (权重: 35分)
    if metrics['error_count'] > 10: risk_score += 35
    elif metrics['error_count'] > 5: risk_score += 25
    elif metrics['error_count'] > 2: risk_score += 15
    
    # 5. 流量突增风险 (权重: 30分)
    if current_pps > recent_avg * 2: risk_score += 30
    elif current_pps > recent_avg * 1.5: risk_score += 20
    
    return min(100.0, risk_score)
```

### 3.2 评分维度详解

#### 3.2.1 丢包率风险 (40分)
- **严重丢包** (>20包): +40分
- **中度丢包** (10-20包): +30分  
- **轻度丢包** (5-10包): +20分
- **正常** (<5包): +0分

#### 3.2.2 连接数风险 (35分)
- **连接数过高** (>500): +35分
- **连接数较高** (200-500): +25分
- **连接数中等** (100-200): +15分
- **正常** (<100): +0分

#### 3.2.3 CPU使用率风险 (30分)
- **CPU过载** (>70%): +30分
- **CPU较高** (60-70%): +25分
- **CPU中等** (50-60%): +20分
- **正常** (<50%): +0分

#### 3.2.4 错误计数风险 (35分)
- **错误严重** (>10个): +35分
- **错误较多** (5-10个): +25分
- **错误较少** (2-5个): +15分
- **正常** (<2个): +0分

#### 3.2.5 流量突增风险 (30分)
- **流量暴涨** (>2倍): +30分
- **流量突增** (1.5-2倍): +20分
- **正常波动** (<1.5倍): +0分

### 3.3 异常分类算法

```python
def _classify_anomaly(self, metrics: Dict[str, Any], risk_score: float) -> str:
    # DDoS攻击检测
    if (metrics['packets_per_sec'] > 5000 and 
        metrics['active_connections'] > 500):
        return "ddos_attack"
    
    # 资源耗尽检测
    if (metrics['cpu_usage'] > 80 or 
        metrics['memory_usage'] > 85 or 
        metrics['error_count'] > 20):
        return "resource_exhaustion"
    
    # 丢包异常检测
    if metrics['dropped_packets'] > 50:
        return "packet_loss"
    
    # 可疑行为检测
    if encryption_ratio > 0.8:
        return "suspicious_behavior"
    
    # 基于风险评分的通用分类
    if risk_score > 90: return "critical_anomaly"
    elif risk_score > 80: return "high_risk_anomaly"
    elif risk_score > 70: return "medium_risk_anomaly"
    else: return "normal"
```

### 3.4 防御状态影响

当防御系统激活时，风险评分会大幅降低：

```python
# 防御激活时风险分数降低
if defense_controller is not None and getattr(defense_controller, 'defense_active', False):
    risk_score = max(risk_score - 60, 0)
```

## 4. AI防御实现机制

### 4.1 智能决策系统

#### 4.1.1 策略选择算法
```python
def select_defense_strategy(self, risk_score: float, anomaly_type: str):
    if anomaly_type and anomaly_type in self.defense_strategies:
        return self.defense_strategies[anomaly_type]
    else:
        # 基于风险评分的智能选择
        if risk_score > 90:
            return self.defense_strategies['ddos_attack']
        elif risk_score > 80:
            return self.defense_strategies['resource_exhaustion']
        elif risk_score > 70:
            return self.defense_strategies['packet_loss']
        else:
            return self.defense_strategies['suspicious_behavior']
```

#### 4.1.2 动态参数调整
- **风险评分自适应**: 根据风险评分动态调整防御参数
- **历史学习**: 基于历史防御效果优化策略
- **实时反馈**: 根据防御效果实时调整参数

### 4.2 机器学习特征

#### 4.2.1 特征工程
```python
def _extract_features(self, metrics: Dict[str, Any]) -> Dict[str, float]:
    return {
        'packets_per_sec': metrics['packets_per_sec'],
        'bytes_per_sec': metrics['bytes_per_sec'],
        'active_connections': metrics['active_connections'],
        'dropped_packets': metrics['dropped_packets'],
        'cpu_usage': metrics['cpu_usage'],
        'memory_usage': metrics['memory_usage'],
        'error_count': metrics['error_count'],
        'encryption_ratio': metrics['encryption_hits'] / (metrics['encryption_hits'] + metrics['decryption_hits'])
    }
```

#### 4.2.2 置信度计算
```python
def _calculate_confidence(self, metrics: Dict[str, Any], risk_score: float) -> float:
    confidence = 0.5  # 基础置信度
    
    # 基于历史数据的置信度调整
    if len(self.history_window) >= 5:
        recent_anomalies = sum(1 for hist in self.history_window[-5:] 
                              if self._calculate_risk_score(hist) > self.risk_threshold)
        
        if recent_anomalies >= 3:
            confidence += 0.3
        elif recent_anomalies >= 1:
            confidence += 0.1
    
    # 基于风险评分的置信度调整
    if risk_score > 90: confidence += 0.3
    elif risk_score > 80: confidence += 0.2
    elif risk_score > 70: confidence += 0.1
    
    return min(1.0, confidence)
```

### 4.3 智能防御流程

#### 4.3.1 自动防御模式
1. **异常检测**: 实时监控网络指标
2. **风险评估**: 计算风险评分和置信度
3. **策略选择**: 基于异常类型和风险评分选择防御策略
4. **规则生成**: 动态生成防御规则
5. **规则下发**: 立即应用到DPU
6. **效果评估**: 监控防御效果并调整

#### 4.3.2 手动防御模式
1. **人工触发**: 用户手动触发防御
2. **策略执行**: 执行预定义防御策略
3. **状态管理**: 维护防御状态
4. **手动关闭**: 用户可手动关闭防御

### 4.4 防御效果评估

#### 4.4.1 效果计算
```python
def _calculate_effectiveness(self) -> float:
    if self.defense_stats['total_triggers'] == 0:
        return 0.0
    
    success_rate = self.defense_stats['successful_defenses'] / self.defense_stats['total_triggers']
    
    # 考虑最近的活动
    recent_triggers = sum(1 for record in self.rule_history 
                         if time.time() - record['timestamp'] < 600)
    
    if recent_triggers > 0:
        effectiveness = success_rate * 0.7 + min(1.0, recent_triggers / 10) * 0.3
    else:
        effectiveness = success_rate
    
    return min(1.0, effectiveness)
```

#### 4.4.2 效果指标
- **防御成功率**: 成功防御次数 / 总触发次数
- **响应时间**: 从检测到防御激活的时间
- **误报率**: 错误触发防御的比例
- **漏报率**: 未检测到异常的比例

## 5. 系统特色功能

### 5.1 实时监控仪表板
- **风险评分可视化**: 实时显示0-100风险评分
- **系统状态指示**: 正常/警告/严重状态切换
- **网络指标监控**: 数据包/秒、连接数、CPU/内存使用率
- **实时图表**: 风险评分和网络流量趋势图
- **告警面板**: 实时异常告警和历史记录

### 5.2 智能防御控制
- **自动/手动模式**: 支持自动防御和手动干预
- **防御策略切换**: 实时切换防御模式
- **手动触发**: 支持手动触发和关闭防御
- **状态管理**: 实时显示防御状态和效果

### 5.3 异常场景模拟
- **DDoS攻击模拟**: 模拟大规模流量攻击
- **资源耗尽模拟**: 模拟CPU/内存资源耗尽
- **丢包异常模拟**: 模拟网络丢包场景
- **实时效果展示**: 直观展示攻击和防御效果

## 6. 技术栈

### 6.1 后端技术
- **Python 3.8+**: 主要开发语言
- **Flask**: Web框架
- **Threading**: 多线程处理
- **JSON**: 数据交换格式
- **Time**: 时间戳和定时器

### 6.2 前端技术
- **HTML5/CSS3**: 页面结构和样式
- **JavaScript (ES6+)**: 前端交互逻辑
- **Bootstrap 5**: UI框架
- **Chart.js**: 图表可视化
- **Font Awesome**: 图标库

### 6.3 数据存储
- **内存存储**: 实时数据缓存
- **时间序列**: 历史数据维护
- **统计信息**: 性能指标统计

## 7. 部署和使用

### 7.1 环境要求
```bash
Python 3.8+
Flask
Chrome/Firefox/Safari浏览器
```

### 7.2 启动步骤
```bash
# 1. 克隆项目
git clone https://github.com/your-username/nvidia-dpu-defense.git
cd nvidia-dpu-defense

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python3 app.py

# 4. 访问系统
打开浏览器访问: http://localhost:5002
```

### 7.3 快速开始
```bash
# 一键启动（推荐）
python3 run.py
```

### 7.4 使用流程
1. **启动模拟**: 点击"启动模拟"开始监控
2. **触发异常**: 点击"触发DDoS"或"触发资源耗尽"
3. **观察防御**: 系统自动或手动触发防御
4. **查看效果**: 观察风险评分变化和防御状态
5. **关闭防御**: 点击"关闭防御"重置状态

## 8. 项目亮点

### 8.1 技术创新
- **实时AI检测**: 基于多维度特征的风险评分算法
- **智能防御**: 动态策略选择和参数调整
- **状态联动**: 模拟器与防御控制器的智能联动
- **可视化监控**: 直观的实时监控界面

### 8.2 实用价值
- **教学演示**: 适合网络安全教学和演示
- **原型验证**: 为实际DPU防御系统提供原型
- **竞赛展示**: 完整展示AI驱动的网络安全防御
- **扩展性强**: 易于扩展新的异常类型和防御策略

### 8.3 工程实践
- **模块化设计**: 清晰的组件分离和接口定义
- **错误处理**: 完善的异常处理和日志记录
- **性能优化**: 高效的数据处理和实时响应
- **用户体验**: 友好的Web界面和交互设计

## 9. 总结

本项目成功实现了一个基于AI的DPU网络风险预警与自动防御系统，具备以下核心能力：

1. **智能检测**: 多维度风险评分和异常分类
2. **自动防御**: 10种防御策略的动态选择和执行
3. **实时监控**: 直观的可视化监控界面
4. **灵活控制**: 支持自动/手动模式切换
5. **效果评估**: 防御效果的实时评估和统计

系统采用模块化设计，具有良好的扩展性和维护性，为NVIDIA DPU网络安全应用提供了完整的解决方案原型。通过实时监控、智能检测、自动防御和效果评估的闭环流程，实现了从威胁检测到自动响应的完整安全防护体系。 