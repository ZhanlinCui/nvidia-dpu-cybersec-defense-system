# AI模型集成指南

## 概述

本项目已集成基于LSTM的AI异常检测模型，用于提升网络异常检测的准确性和预测能力。AI模型可以与现有的规则检测系统协同工作，形成混合检测架构。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装AI模型依赖
pip install -r requirements_ai.txt

# 或者单独安装核心依赖
pip install torch numpy pandas scikit-learn
```

### 2. 训练AI模型

```bash
# 使用合成数据训练模型
python train_ai_model.py --mode both

# 仅训练模型
python train_ai_model.py --mode train --epochs 100

# 仅测试模型
python train_ai_model.py --mode test --model-path models/anomaly_lstm.pth
```

### 3. 集成到现有系统

```bash
# 运行集成脚本
python integrate_ai_detector.py
```

### 4. 启动系统

```bash
# 启动应用服务器
python app.py
```

## 📁 文件结构

```
src/ai_engine/
├── models/
│   └── simple_lstm.py          # LSTM模型定义
├── training/
│   └── data_processor.py       # 数据预处理
└── inference/
    ├── anomaly_detector.py     # 原有检测器
    └── ai_anomaly_detector.py  # AI检测器

models/                          # 模型文件目录
├── anomaly_lstm.pth            # 训练好的模型
└── usage_info.json             # 使用说明

configs/                         # 配置文件
└── ai_model_config.json        # AI模型配置

train_ai_model.py               # 模型训练脚本
integrate_ai_detector.py        # 集成脚本
```

## 🧠 AI模型架构

### LSTM模型结构

```python
class SimpleLSTM(nn.Module):
    def __init__(self, config):
        # LSTM层: 输入9个特征，64个隐藏单元，2层
        self.lstm = nn.LSTM(
            input_size=9,        # 网络指标特征数
            hidden_size=64,      # 隐藏层大小
            num_layers=2,        # LSTM层数
            dropout=0.2,         # Dropout率
            batch_first=True
        )
        
        # 全连接层: 64 -> 32 -> 1
        self.fc = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid()         # 输出0-1异常分数
        )
```

### 输入特征

模型使用9个网络指标作为输入特征：

1. `packets_per_sec` - 每秒数据包数
2. `bytes_per_sec` - 每秒字节数
3. `active_connections` - 活跃连接数
4. `dropped_packets` - 丢包数
5. `encryption_hits` - 加密命中数
6. `decryption_hits` - 解密命中数
7. `cpu_usage` - CPU使用率
8. `memory_usage` - 内存使用率
9. `error_count` - 错误计数

### 时间序列处理

- **序列长度**: 10个时间步
- **滑动窗口**: 实时更新
- **数据标准化**: 自动计算均值和标准差

## 🔧 配置说明

### 模型配置 (configs/ai_model_config.json)

```json
{
  "model": {
    "input_size": 9,
    "hidden_size": 64,
    "num_layers": 2,
    "sequence_length": 10,
    "dropout": 0.2,
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100
  },
  "detection": {
    "risk_threshold": 0.7,
    "confidence_threshold": 0.6,
    "update_interval": 1.0
  },
  "anomaly_types": {
    "ddos_attack": {"threshold": 0.8, "weight": 1.0},
    "resource_exhaustion": {"threshold": 0.7, "weight": 0.8},
    "packet_loss": {"threshold": 0.6, "weight": 0.6},
    "suspicious_behavior": {"threshold": 0.5, "weight": 0.7}
  }
}
```

## 🎯 检测模式

### 1. 混合模式 (Hybrid)
- **权重**: 规则检测30% + AI检测70%
- **优势**: 结合规则的可解释性和AI的准确性
- **适用**: 生产环境推荐

### 2. 仅规则检测 (Rule Only)
- **权重**: 100%规则检测
- **优势**: 可解释性强，响应快速
- **适用**: AI模型不可用时

### 3. 仅AI检测 (AI Only)
- **权重**: 100%AI检测
- **优势**: 检测准确性高，可发现复杂模式
- **适用**: 模型训练充分时

## 📊 API接口

### 获取AI检测器状态
```http
GET /api/ai/status
```

响应:
```json
{
  "detection_mode": "hybrid",
  "rule_weight": 0.3,
  "ai_weight": 0.7,
  "ai_model_loaded": true,
  "ai_model_version": "1.0.0",
  "history_size": 50
}
```

### 设置检测模式
```http
POST /api/ai/mode
Content-Type: application/json

{
  "mode": "hybrid"
}
```

### 设置检测权重
```http
POST /api/ai/weights
Content-Type: application/json

{
  "rule_weight": 0.3,
  "ai_weight": 0.7
}
```

### 获取检测历史
```http
GET /api/ai/history?window_size=50
```

## 🎨 Web界面

在dashboard.html中添加AI检测器控制面板：

```html
<div class="ai-control-panel">
    <h3>AI检测器控制</h3>
    
    <div class="control-group">
        <label>检测模式:</label>
        <select id="detectionMode" onchange="setDetectionMode()">
            <option value="hybrid">混合模式</option>
            <option value="rule_only">仅规则检测</option>
            <option value="ai_only">仅AI检测</option>
        </select>
    </div>
    
    <div class="control-group">
        <label>规则权重:</label>
        <input type="range" id="ruleWeight" min="0" max="1" step="0.1" value="0.3">
        <span id="ruleWeightValue">0.3</span>
    </div>
    
    <div class="control-group">
        <label>AI权重:</label>
        <input type="range" id="aiWeight" min="0" max="1" step="0.1" value="0.7">
        <span id="aiWeightValue">0.7</span>
    </div>
</div>
```

## 🔄 使用流程

### 1. 数据收集
```python
from src.ai_engine.training.data_processor import DataProcessor

# 创建数据处理器
processor = DataProcessor(sequence_length=10)

# 添加网络指标
processor.add_metrics(metrics, is_anomaly=False)
```

### 2. 模型训练
```python
from src.ai_engine.models.simple_lstm import AnomalyPredictor, ModelConfig

# 创建模型配置
config = ModelConfig(
    input_size=9,
    hidden_size=64,
    num_layers=2,
    sequence_length=10
)

# 创建预测器
predictor = AnomalyPredictor(config)

# 训练模型
history = predictor.train(train_data, train_labels, val_data, val_labels)
```

### 3. 实时检测
```python
from src.ai_engine.inference.ai_anomaly_detector import AIAnomalyDetector

# 创建AI检测器
detector = AIAnomalyDetector(model_path="models/anomaly_lstm.pth")

# 检测异常
result = detector.detect_anomaly(metrics)
print(f"风险评分: {result.risk_score}")
print(f"是否异常: {result.is_anomaly}")
```

## 📈 性能优化

### 1. 模型优化
- **量化**: 使用INT8量化减少模型大小
- **剪枝**: 移除不重要的连接
- **蒸馏**: 训练更小的学生模型

### 2. 推理优化
- **批处理**: 批量处理多个请求
- **缓存**: 缓存中间计算结果
- **并行**: 多线程并行推理

### 3. 硬件加速
- **GPU**: 使用CUDA加速训练和推理
- **TensorRT**: 优化推理性能
- **ONNX**: 跨平台模型部署

## 🐛 故障排除

### 常见问题

1. **模型加载失败**
   ```bash
   # 检查模型文件是否存在
   ls -la models/anomaly_lstm.pth
   
   # 重新训练模型
   python train_ai_model.py --mode train
   ```

2. **内存不足**
   ```python
   # 减少批次大小
   config.batch_size = 16
   
   # 减少隐藏层大小
   config.hidden_size = 32
   ```

3. **训练速度慢**
   ```python
   # 减少训练轮数
   config.epochs = 50
   
   # 使用GPU加速
   device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
   ```

### 日志调试

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看详细日志
logger = logging.getLogger(__name__)
logger.debug("调试信息")
```

## 🔮 未来扩展

### 1. 模型改进
- **Transformer**: 使用注意力机制
- **Graph Neural Networks**: 网络拓扑分析
- **Autoencoder**: 无监督异常检测

### 2. 特征工程
- **统计特征**: 均值、方差、偏度等
- **频域特征**: FFT变换
- **图特征**: 网络连接模式

### 3. 集成学习
- **Ensemble**: 多个模型投票
- **Stacking**: 模型堆叠
- **Boosting**: 梯度提升

## 📚 参考资料

- [PyTorch官方文档](https://pytorch.org/docs/)
- [LSTM网络教程](https://pytorch.org/tutorials/beginner/nlp/sequence_models_tutorial.html)
- [时间序列异常检测](https://arxiv.org/abs/2004.00431)
- [网络流量分析](https://ieeexplore.ieee.org/document/1234567)

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。 