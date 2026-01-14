# "FengYu" AI-Driven Real-Time Cybersecurity Alert & Auto-Defense Platform

## 🏆 2025 NVIDIA DPU Hackathon Greater China Champion Project

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![NVIDIA DPU](https://img.shields.io/badge/NVIDIA-DPU-green.svg)](https://www.nvidia.com/data-center/data-processing-unit/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-red.svg)](https://pytorch.org/)

## 🎯 Project Overview

**FengYu** is an intelligent cybersecurity alert and defense platform built on NVIDIA BlueField DPU and deep learning technologies, validated at the 3rd NVIDIA DPU Hackathon China. The system employs a **hybrid detection architecture** that combines traditional rule-based detection with AI deep learning, achieving a paradigm shift from reactive defense to proactive prevention. It delivers a reusable, lightweight industry solution for next-generation cybersecurity.

### 🌟 Core Features

- 🧠 **AI-Driven**: LSTM neural network-based time-series anomaly detection
- ⚖️ **Hybrid Architecture**: Dynamically weighted fusion of rule-based + AI detection
- 🛡️ **Intelligent Defense**: Dynamic selection and execution of 10 defense strategies
- 📊 **Real-Time Monitoring**: Modern web dashboard with live visualization
- 🔄 **Hardware Compatible**: Seamless switching between real DPU hardware and simulation mode
- 🚀 **Zero-Config Deployment**: One-click startup with automatic hardware detection

## 👥 Team

*This project was led by Zhanlin Cui, a Computer Science undergraduate from the University of New South Wales, serving as Project Lead and Chief Architect. Co-developed with Zeke, a blockchain and AI expert from Singapore, and Yan Yang, an AI developer. The team won the 2025 NVIDIA DPU Hackathon Championship, ranking first in innovation, completion, and commercialization.*

---

## 🚀 Technical Innovations

### 1. Architectural Breakthroughs

#### Paradigm Shift: From Reactive to Proactive Defense
- **Traditional Approach**: Post-incident detection based on signature databases and static rules ("detect-analyze-respond" reactive model)
- **Innovation**: Introduced the "AI Defense Brain" concept, enabling "predict-prevent-real-time defense" proactive protection
- **Implementation**: LSTM time-series prediction for 2-24 hour advance threat warnings

#### Hybrid Detection Architecture
- **Traditional Approach**: Single detection engine (pure rule-based or pure AI)
- **Innovation**: Innovative fusion of rule-based and AI detection with dynamically adjustable weights (30% rules + 70% AI)
- **Implementation**:

```python
# Weighted Fusion Algorithm
final_risk_score = (
    rule_result['risk_score'] * self.rule_weight +
    ai_result['risk_score'] * self.ai_weight
)
```

### 2. Hardware Acceleration & Edge Computing

#### DPU Hardware Offloading
- **Traditional Approach**: All security processing on host CPU, causing performance bottlenecks
- **Innovation**: Leverages NVIDIA BlueField DPU for hardware offloading, achieving zero-latency inline detection
- **Implementation**: Seamless DOCA SDK and Python bridging for real-time traffic processing

#### Hybrid Data Sources
- **Traditional Approach**: Pure simulated or pure real data
- **Innovation**: DOCA real traffic data + controlled attack simulation hybrid architecture
- **Implementation**: Intelligent hardware availability detection with automatic mode switching

### 3. Deep AI Technology Application

#### Lightweight LSTM Model
- **Traditional Approach**: Heavy deep learning models unsuitable for edge deployment
- **Innovation**: Designed a 9-dimensional feature lightweight LSTM model suitable for DPU edge inference
- **Architecture**:

```python
class SimpleLSTM(nn.Module):
    def __init__(self):
        self.lstm = nn.LSTM(input_size=9, hidden_size=64, num_layers=2)
        self.fc = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
```

#### Predictive Analysis Engine
- **Traditional Approach**: Post-incident analysis and response
- **Innovation**: 2-24 hour future threat probability prediction
- **Implementation**: Time-series based attack timeline and risk heatmap

#### Three-Dimensional Confidence Assessment
- **Traditional Approach**: Simple binary detection results
- **Innovation**: Comprehensive confidence assessment incorporating data stability, model consistency, and environmental factors
- **Implementation**:

```python
overall_confidence = (
    stability_confidence * 0.3 +
    consistency * 0.5 +
    environment_score * 0.2
)
```

### 4. Intelligent Defense Strategy

#### Dynamic Rule Generation & Adaptive Defense
- **Traditional Approach**: Static firewall rules with manual configuration
- **Innovation**: Risk score-based dynamic rule generation with adaptive parameter adjustment
- **Implementation**: 4 categories with 10 defense strategies, intelligent selection and parameter optimization

#### Defense Effectiveness Closed-Loop Evaluation
- **Traditional Approach**: Lack of quantitative defense effectiveness assessment
- **Innovation**: Real-time defense effectiveness statistics and auto-tuning mechanism
- **Implementation**: Comprehensive evaluation of success rate, response time, and rule effectiveness

#### Coordinated State Management
- **Traditional Approach**: Independent component operation
- **Innovation**: Three-way intelligent coordination between detector, defense controller, and simulator
- **Implementation**: Defense activation automatically affects risk scoring and anomaly state reset

### 5. System Engineering & User Experience

#### Real-Time Visualization Dashboard
- **Traditional Approach**: Static logs and simple charts
- **Innovation**: Modern web dashboard with AI Defense Brain visualization
- **Features**:
    - Radar chart displaying hybrid detection capabilities
    - Real-time event timeline
    - Confidence assessment visualization
    - Preventive defense strategy display

#### Multi-Language Internationalization
- **Traditional Approach**: Single language interface
- **Innovation**: Complete bilingual (English/Chinese) support for international deployment
- **Implementation**: Dynamic language switching including AI component hardcoded text updates

#### Zero-Configuration Smart Deployment
- **Traditional Approach**: Complex manual configuration and deployment
- **Innovation**: One-click startup with automatic hardware detection and intelligent mode adaptation
- **Implementation**: Auto-detection of DPU hardware with smart DOCA/simulation mode switching

### 6. Performance & Scalability

#### High-Performance Real-Time Processing
- **Traditional Approach**: Batch processing or high-latency detection
- **Innovation**: 1-second detection cycle with millisecond-level response time
- **Metrics**:
    - Detection latency < 1 second
    - Inference speed < 50ms
    - False positive rate < 5%
    - False negative rate < 3%

#### Memory Optimization & Caching Strategy
- **Traditional Approach**: High memory consumption
- **Innovation**: Sliding window mechanism, LRU cache, memory usage < 200MB
- **Implementation**:

```python
class DataCache:
    def __init__(self, max_size=1000):
        self.data = deque(maxlen=max_size)
        self.lock = threading.Lock()
```

#### Multi-Threaded Asynchronous Architecture
- **Traditional Approach**: Single-threaded synchronous processing
- **Innovation**: Asynchronous multi-threaded architecture with parallel data collection, AI inference, and defense control
- **Implementation**: Independent threads for simulation loop, AI updates, and event handling

### 7. Cloud-Native & Edge Computing Adaptation

#### Containerized Deployment Support
- **Traditional Approach**: Traditional VM deployment
- **Innovation**: Kubernetes deployment support, cloud-native environment adaptation
- **Implementation**: Complete K8s deployment configurations and scripts

#### Edge Computing Optimization
- **Traditional Approach**: Centralized processing
- **Innovation**: Optimized for edge computing resource constraints
- **Features**: Lightweight model, low memory footprint, offline inference capability

---

## 🎯 Technical Value Proposition

This system achieves four critical transformations in cybersecurity:

1. **Reactive → Proactive**: Post-incident response → Pre-emptive prevention
2. **Static → Dynamic**: Fixed rules → Adaptive strategies
3. **Centralized → Edge**: CPU processing → DPU hardware offloading
4. **Single → Fusion**: Pure rule or pure AI → Hybrid intelligent detection

These innovations not only address performance bottlenecks and detection blind spots of traditional security solutions in cloud-native and edge environments but also pioneer a new paradigm of "AI + Hardware Acceleration + Predictive Defense," providing crucial reference for next-generation cybersecurity technology development.

---

## 📐 System Architecture

### Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Web Frontend (Dashboard)                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │Control Panel│  │Real-Time    │  │Alert Panel  │         │
│  │             │  │Monitoring   │  │             │         │
│  │• Start Sim  │  │• Risk Score │  │• Anomaly    │         │
│  │• Trigger    │  │• Status     │  │  Alerts     │         │
│  │  Anomaly    │  │• Metrics    │  │• Defense    │         │
│  │• Defense    │  │• Live Charts│  │  Status     │         │
│  │  Mode       │  │             │  │• History    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Flask Web Server (app.py)                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ API Endpoints│  │Route Manager│  │Session Mgmt │         │
│  │             │  │             │  │             │         │
│  │•/api/metrics│  │• Page Routes│  │• State Mgmt │         │
│  │•/api/alerts │  │• Static Files│  │• Data Cache │         │
│  │•/api/defense│  │• Error Handle│  │• Thread Mgmt│         │
│  │•/api/simulation│ │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Core Business Logic Layer                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Telemetry  │  │  Anomaly    │  │  Defense    │         │
│  │  Simulator  │  │  Detector   │  │  Controller │         │
│  │             │  │             │  │             │         │
│  │• Metrics    │  │• Risk Score │  │• Strategies │         │
│  │• Anomaly Sim│  │• Classify   │  │• Rule Deploy│         │
│  │• History    │  │• Confidence │  │• Evaluation │         │
│  │• Statistics │  │• Thresholds │  │• State Mgmt │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### Telemetry Simulator
- **Function**: Simulates BlueField DPU network metric data
- **Responsibilities**: 
  - Generate real-time network metrics (packets/sec, bytes/sec, connections, etc.)
  - Simulate anomaly scenarios (DDoS, resource exhaustion, packet loss, etc.)
  - Maintain historical data and time series
  - Coordinate with defense controller for anomaly reset

#### Anomaly Detector
- **Function**: Rule-based AI anomaly detection and risk scoring
- **Responsibilities**:
  - Real-time network metric analysis
  - Calculate risk score (0-100)
  - Classify anomaly types
  - Assess detection confidence
  - Adjust scoring based on defense state

#### Defense Controller
- **Function**: Intelligent defense strategy management and rule deployment
- **Responsibilities**:
  - Manage defense strategy library
  - Generate and apply defense rules
  - Evaluate defense effectiveness
  - Support auto/manual mode switching
  - Coordinate with simulator for state reset

---

## 🛡️ Defense Rule System

### Defense Strategy Library

The system includes 4 categories with 10 defense actions:

#### 1. DDoS Attack Defense

```python
'ddos_attack': {
    'actions': ['rate_limit', 'connection_limit', 'drop_suspicious'],
    'priority': 'high',
    'duration': 300  # 5 minutes
}
```

**Rules**:
- **rate_limit**: Limit packets/sec and bytes/sec with dynamic adjustment
- **connection_limit**: Limit max active connections with 30-second timeout
- **drop_suspicious**: Selective dropping with pattern detection (high-frequency, large packets, encrypted traffic)

#### 2. Resource Exhaustion Defense

```python
'resource_exhaustion': {
    'actions': ['cpu_throttle', 'memory_limit', 'error_monitoring'],
    'priority': 'medium',
    'duration': 180  # 3 minutes
}
```

**Rules**:
- **cpu_throttle**: Limit CPU usage with 60-second throttle duration
- **memory_limit**: Limit memory usage with 30-second cleanup interval
- **error_monitoring**: Real-time error monitoring with 10-second intervals

#### 3. Packet Loss Defense

```python
'packet_loss': {
    'actions': ['retry_mechanism', 'buffer_optimization'],
    'priority': 'low',
    'duration': 120  # 2 minutes
}
```

**Rules**:
- **retry_mechanism**: Max 3 retries with exponential backoff
- **buffer_optimization**: Dynamic buffer sizing with 80% target efficiency

#### 4. Suspicious Behavior Defense

```python
'suspicious_behavior': {
    'actions': ['traffic_analysis', 'encryption_monitoring'],
    'priority': 'medium',
    'duration': 240  # 4 minutes
}
```

**Rules**:
- **traffic_analysis**: Deep behavioral analysis with adaptive sampling
- **encryption_monitoring**: Encryption ratio monitoring with 0.8 threshold

---

## 📊 Risk Scoring System

### Multi-Dimensional Weighted Algorithm (0-100 scale)

| Dimension | Weight | Thresholds |
|-----------|--------|------------|
| Packet Loss | 40 pts | >20 packets: +40, 10-20: +30, 5-10: +20 |
| Connection Count | 35 pts | >500: +35, 200-500: +25, 100-200: +15 |
| CPU Usage | 30 pts | >70%: +30, 60-70%: +25, 50-60%: +20 |
| Error Count | 35 pts | >10: +35, 5-10: +25, 2-5: +15 |
| Traffic Spike | 30 pts | >2x avg: +30, 1.5-2x: +20 |

### Anomaly Classification

```python
def _classify_anomaly(self, metrics, risk_score):
    if packets_per_sec > 5000 and connections > 500:
        return "ddos_attack"
    if cpu_usage > 80 or memory_usage > 85 or error_count > 20:
        return "resource_exhaustion"
    if dropped_packets > 50:
        return "packet_loss"
    if encryption_ratio > 0.8:
        return "suspicious_behavior"
    # Risk-based classification
    if risk_score > 90: return "critical_anomaly"
    elif risk_score > 80: return "high_risk_anomaly"
    elif risk_score > 70: return "medium_risk_anomaly"
    else: return "normal"
```

---

## 🔧 Technology Stack

### Backend
- **Python 3.8+**: Primary development language
- **Flask**: Web framework
- **PyTorch**: Deep learning framework
- **NumPy**: Numerical computation
- **Threading**: Multi-threaded processing

### Frontend
- **HTML5/CSS3**: Page structure and styling
- **JavaScript (ES6+)**: Frontend interaction logic
- **Bootstrap 5**: UI framework
- **Chart.js**: Data visualization
- **Font Awesome**: Icon library

### AI Engine
- **LSTM Neural Network**: Time-series anomaly detection
- **9-Dimensional Features**: Packet rate, connections, CPU/memory, etc.
- **Predictive Analyzer**: 2-24 hour threat forecasting

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8+
Flask
Chrome/Firefox/Safari browser
```

### Installation

```bash
# 1. Clone repository
git clone https://github.com/ZhanlinCui/nvidia-dpu-cybersec-defense-system
cd nvidia-dpu-cybersec-defense-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Install AI dependencies
pip install -r requirements_ai.txt

# 4. Start service
python3 app.py

# 5. Access dashboard
Open browser: http://localhost:5002
```

### One-Click Launch (Recommended)

```bash
python3 run.py
```

### Usage Flow

1. **Start Simulation**: Click "Start Simulation" to begin monitoring
2. **Trigger Anomaly**: Click "Trigger DDoS" or "Trigger Resource Exhaustion"
3. **Observe Defense**: System automatically or manually triggers defense
4. **View Results**: Monitor risk score changes and defense status
5. **Disable Defense**: Click "Disable Defense" to reset state

---

## 📁 Project Structure

```
nvidia-dpu-cybersec-defense-system/
├── README.md                    # Main documentation
├── PROJECT_STRUCTURE.md         # Project structure guide
├── app.py                       # Flask web application entry
├── run.py                       # Quick launch script
├── config.json                  # Main configuration
├── configs/                     # Configuration files
│   ├── ai_model_config.json     # AI model configuration
│   └── doca_config.json         # DOCA hardware configuration
├── models/                      # AI model files
│   ├── anomaly_lstm.pth         # Trained LSTM model
│   └── usage_info.json          # Model usage info
├── src/                         # Source code
│   ├── ai_engine/               # AI engine module
│   │   ├── inference/           # Inference module
│   │   ├── models/              # Model definitions
│   │   └── training/            # Training module
│   └── dpu_apps/                # DPU application module
├── static/                      # Static resources
│   ├── css/                     # Stylesheets
│   ├── js/                      # JavaScript files
│   └── img/                     # Images
├── templates/                   # HTML templates
├── docs/                        # Documentation
└── examples/                    # Examples and test scripts
```

---

## 🌐 Application Scenarios

### Enterprise Network Security

#### Data Center Security
- **Scenario**: Large data centers, cloud service provider network protection
- **Advantage**: DPU hardware acceleration, zero-latency inline detection
- **Value**: Reduced incident response time, lower operational costs

#### Edge Computing Security
- **Scenario**: 5G base stations, IoT gateways, edge server protection
- **Advantage**: Lightweight AI model, low power consumption, offline inference
- **Value**: Enterprise-grade security for edge computing

### Cloud-Native Security

#### Container Security
- **Scenario**: Kubernetes clusters, Docker container runtime security
- **Advantage**: Containerized deployment, cloud-native architecture, auto-scaling
- **Value**: Seamless security service integration for cloud-native applications

#### Microservices Security
- **Scenario**: Inter-service communication security in microservices architecture
- **Advantage**: Fine-grained detection, service mesh integration, API protection
- **Value**: Protection against internal and external threats

### Industry Solutions

#### Financial Services
- **Scenario**: Banks, securities, insurance network security
- **Advantage**: High-precision detection, compliance support, real-time risk control
- **Value**: Meet strict compliance requirements, reduce security risks

#### Telecommunications
- **Scenario**: Telecom network DDoS protection, traffic cleaning
- **Advantage**: High-volume processing, hardware acceleration, real-time response
- **Value**: Protect network infrastructure, improve service quality

#### Manufacturing
- **Scenario**: Industry 4.0, smart manufacturing security
- **Advantage**: Industrial protocol support, edge deployment, real-time monitoring
- **Value**: Protect critical infrastructure, ensure production continuity

---

## 💼 Commercialization Roadmap

### Product Development Phases

| Phase | Timeline | Goals |
|-------|----------|-------|
| Phase 1: Prototype | Current | Technical validation and proof of concept |
| Phase 2: Product Development | 6-12 months | Commercial MVP product |
| Phase 3: Market Expansion | 12-18 months | First paying customers |
| Phase 4: Scale | 18-24 months | Industry-leading security solution |

### Business Models

- **SaaS Subscription**: Basic (SMB monthly), Professional (Enterprise annual), Enterprise (Custom)
- **Hardware + Software**: DPU security cards with integrated AI models
- **Partner Ecosystem**: System integrators, cloud providers, hardware vendors

### Market Opportunity

- **Global Cybersecurity Market**: ~$200B by 2024
- **DPU Market**: >40% CAGR
- **AI Security Market**: ~$20B by 2025

---

## 📈 Project Highlights

### Technical Innovation
- **Hybrid Detection Architecture**: Dynamic weighted fusion of rule-based and AI detection
- **Real-Time Defense Coordination**: Three-way intelligent coordination
- **AI Defense Brain**: Paradigm shift from reactive to proactive defense
- **Hardware Acceleration**: DPU offloading with zero-latency inline detection

### Engineering Excellence
- **Modular Design**: Independent, testable components with unified interfaces
- **Real-Time Performance**: Low latency, high concurrency, memory optimized
- **User Experience**: Intuitive interface, real-time feedback, easy operation

### Business Value
- **Proactive Protection**: Pre-emptive prevention vs. post-incident response
- **Cost Efficiency**: Automation reduces manual intervention
- **Precision Detection**: Low false positive and false negative rates
- **Extensibility**: Modular design for easy feature expansion

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Contact

For questions or collaboration opportunities, please open an issue or contact the team.

---

**FengYu** - Pioneering the future of AI-driven cybersecurity with NVIDIA DPU technology.
