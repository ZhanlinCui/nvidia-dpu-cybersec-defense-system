# Project Structure

## 📁 Directory Structure

```
nvidia-dpu-cybersec-defense-system/
├── README.md                    # Main documentation
├── PROJECT_STRUCTURE.md         # Project structure guide
├── .gitignore                   # Git ignore configuration
├── requirements.txt             # Base dependencies
├── requirements_ai.txt          # AI model dependencies
├── config.json                  # Main configuration file
├── app.py                       # Flask web application entry
├── run.py                       # Quick launch script
│
├── configs/                     # Configuration directory
│   ├── ai_model_config.json     # AI model configuration
│   └── doca_config.json         # DOCA hardware configuration
│
├── models/                      # AI model files
│   ├── anomaly_lstm.pth         # Trained LSTM model
│   └── usage_info.json          # Model usage information
│
├── src/                         # Source code directory
│   ├── ai_engine/               # AI engine module
│   │   ├── inference/           # Inference module
│   │   │   ├── ai_anomaly_detector.py    # AI anomaly detector
│   │   │   ├── anomaly_detector.py       # TensorRT inference service
│   │   │   └── predictive_analyzer.py    # Predictive analyzer
│   │   ├── models/              # Model definitions
│   │   │   └── simple_lstm.py   # LSTM model implementation
│   │   └── training/            # Training module
│   │       └── data_processor.py # Data processor
│   │
│   ├── dpu_apps/                # DPU application module
│   │   └── telemetry/           # Telemetry data collection
│   │       └── telemetry_collector.c  # C telemetry collector
│   │
│   └── host_apps/               # Host application module
│
├── static/                      # Static resources
│   ├── css/
│   │   └── dashboard.css        # Dashboard styles
│   ├── js/
│   │   ├── dashboard.js         # Dashboard interaction logic
│   │   └── i18n.js              # Internationalization support
│   └── img/
│       ├── background.jpg       # Background image
│       └── logo.png             # Project logo
│
├── templates/                   # HTML templates
│   └── dashboard.html           # Main dashboard page
│
├── docs/                        # Documentation directory
│   ├── competition_guide.md     # Competition guide
│   └── development_without_hardware.md  # Development guide without hardware
│
└── examples/                    # Examples and test scripts
    ├── test_ai_model.py         # AI model test script
    └── train_ai_model.py        # AI model training script
```

## 🔧 Core Components

### Main Application Files
- **app.py**: Flask web application entry, provides REST API and web interface
- **run.py**: Quick launch script with automatic environment detection
- **config.json**: Main configuration file with system runtime parameters

### Core Business Logic
- **anomaly_detector.py**: Rule-based anomaly detector
- **integrate_ai_detector.py**: Hybrid AI detector (rule + AI fusion)
- **defense_controller.py**: Intelligent defense controller
- **telemetry_simulator.py**: Telemetry data simulator

### AI Engine Module
- **simple_lstm.py**: Lightweight LSTM model implementation
- **ai_anomaly_detector.py**: AI anomaly detection inference service
- **predictive_analyzer.py**: Predictive analysis engine
- **data_processor.py**: Data preprocessing and feature engineering

### Frontend Interface
- **dashboard.html**: Modern web dashboard
- **dashboard.js**: Real-time data updates and interaction logic
- **dashboard.css**: Responsive style design
- **i18n.js**: English/Chinese bilingual support

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Install base dependencies
pip install -r requirements.txt

# Install AI model dependencies (optional)
pip install -r requirements_ai.txt
```

### 2. Start System

```bash
# Method 1: Quick launch
python3 run.py

# Method 2: Standard launch
python3 app.py
```

### 3. Access Interface

Open browser: http://localhost:5002

## 📝 Development Guide

### Adding New Detection Rules
1. Modify risk scoring algorithm in `anomaly_detector.py`
2. Update defense strategies in `defense_controller.py`
3. Add corresponding visualization in `dashboard.js`

### Training New AI Models
1. Use `examples/train_ai_model.py` to train model
2. Save trained model to `models/` directory
3. Update `configs/ai_model_config.json` configuration

### Extending Defense Strategies
1. Add new defense actions in `defense_controller.py`
2. Update defense strategy configuration
3. Test defense effectiveness

## 🔍 File Descriptions

### Configuration Files
- `config.json`: System main configuration
- `configs/ai_model_config.json`: AI model parameter configuration
- `configs/doca_config.json`: DPU hardware configuration

### Model Files
- `models/anomaly_lstm.pth`: Pre-trained LSTM anomaly detection model
- `models/usage_info.json`: Model usage statistics

### Documentation Files
- `README.md`: Main project documentation
- `docs/competition_guide.md`: Competition participation guide
- `docs/development_without_hardware.md`: Development guide without hardware

## 🎯 Project Features

1. **Modular Design**: Clear component separation, easy to maintain and extend
2. **Hybrid Detection**: Intelligent fusion of rule-based and AI detection
3. **Real-Time Performance**: 1-second detection cycle, millisecond-level response
4. **Visual Interface**: Modern web dashboard with real-time monitoring
5. **Hardware Compatible**: Support for real DPU and simulation mode
6. **Internationalization**: English/Chinese bilingual support
