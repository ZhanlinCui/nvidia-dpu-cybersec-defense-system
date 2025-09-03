# 项目结构说明

## 📁 项目目录结构

```
nvidia-dpu-cybersec-defense-system/
├── README.md                    # 项目主要文档
├── PROJECT_STRUCTURE.md         # 项目结构说明
├── .gitignore                   # Git忽略文件配置
├── requirements.txt             # 基础依赖
├── requirements_ai.txt          # AI模型依赖
├── config.json                  # 主配置文件
├── app.py                       # Flask Web应用主入口
├── run.py                       # 快速启动脚本
│
├── configs/                     # 配置文件目录
│   ├── ai_model_config.json     # AI模型配置
│   └── doca_config.json         # DOCA硬件配置
│
├── models/                      # AI模型文件
│   ├── anomaly_lstm.pth         # 训练好的LSTM模型
│   └── usage_info.json          # 模型使用信息
│
├── src/                         # 源代码目录
│   ├── ai_engine/               # AI引擎模块
│   │   ├── inference/           # 推理模块
│   │   │   ├── ai_anomaly_detector.py    # AI异常检测器
│   │   │   ├── anomaly_detector.py       # TensorRT推理服务
│   │   │   └── predictive_analyzer.py    # 预测性分析器
│   │   ├── models/              # 模型定义
│   │   │   └── simple_lstm.py   # LSTM模型实现
│   │   └── training/            # 训练模块
│   │       └── data_processor.py # 数据处理器
│   │
│   ├── dpu_apps/                # DPU应用模块
│   │   └── telemetry/           # 遥测数据收集
│   │       └── telemetry_collector.c  # C语言遥测收集器
│   │
│   └── host_apps/               # 主机应用模块
│
├── static/                      # 静态资源
│   ├── css/
│   │   └── dashboard.css        # 仪表板样式
│   ├── js/
│   │   ├── dashboard.js         # 仪表板交互逻辑
│   │   └── i18n.js              # 国际化支持
│   └── img/
│       ├── background.jpg       # 背景图片
│       └── logo.png             # 项目Logo
│
├── templates/                   # HTML模板
│   └── dashboard.html           # 主仪表板页面
│
├── docs/                        # 文档目录
│   ├── competition_guide.md     # 竞赛指南
│   └── development_without_hardware.md  # 无硬件开发指南
│
└── examples/                    # 示例和测试脚本
    ├── test_ai_model.py         # AI模型测试脚本
    └── train_ai_model.py        # AI模型训练脚本
```

## 🔧 核心组件说明

### 主要应用文件
- **app.py**: Flask Web应用主入口，提供REST API和Web界面
- **run.py**: 快速启动脚本，自动检测环境并启动服务
- **config.json**: 主配置文件，包含系统运行参数

### 核心业务逻辑
- **anomaly_detector.py**: 基于规则的异常检测器
- **integrate_ai_detector.py**: 混合AI检测器（规则+AI融合）
- **defense_controller.py**: 智能防御控制器
- **telemetry_simulator.py**: 遥测数据模拟器

### AI引擎模块
- **simple_lstm.py**: 轻量化LSTM模型实现
- **ai_anomaly_detector.py**: AI异常检测推理服务
- **predictive_analyzer.py**: 预测性分析引擎
- **data_processor.py**: 数据预处理和特征工程

### 前端界面
- **dashboard.html**: 现代化Web仪表板
- **dashboard.js**: 实时数据更新和交互逻辑
- **dashboard.css**: 响应式样式设计
- **i18n.js**: 中英文双语支持

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装AI模型依赖（可选）
pip install -r requirements_ai.txt
```

### 2. 启动系统
```bash
# 方式1: 快速启动
python3 run.py

# 方式2: 标准启动
python3 app.py
```

### 3. 访问界面
打开浏览器访问: http://localhost:5002

## 📝 开发指南

### 添加新的检测规则
1. 修改 `anomaly_detector.py` 中的风险评分算法
2. 更新 `defense_controller.py` 中的防御策略
3. 在 `dashboard.js` 中添加相应的可视化

### 训练新的AI模型
1. 使用 `examples/train_ai_model.py` 训练模型
2. 将训练好的模型保存到 `models/` 目录
3. 更新 `configs/ai_model_config.json` 配置

### 扩展防御策略
1. 在 `defense_controller.py` 中添加新的防御动作
2. 更新防御策略配置
3. 测试防御效果

## 🔍 文件说明

### 配置文件
- `config.json`: 系统主配置
- `configs/ai_model_config.json`: AI模型参数配置
- `configs/doca_config.json`: DPU硬件配置

### 模型文件
- `models/anomaly_lstm.pth`: 预训练的LSTM异常检测模型
- `models/usage_info.json`: 模型使用统计信息

### 文档文件
- `README.md`: 项目主要文档
- `docs/competition_guide.md`: 竞赛参与指南
- `docs/development_without_hardware.md`: 无硬件开发指南

## 🎯 项目特色

1. **模块化设计**: 清晰的组件分离，易于维护和扩展
2. **混合检测**: 规则检测与AI检测的智能融合
3. **实时性能**: 1秒检测周期，毫秒级响应
4. **可视化界面**: 现代化Web仪表板，实时监控
5. **硬件兼容**: 支持真实DPU和模拟模式
6. **国际化**: 中英文双语支持
