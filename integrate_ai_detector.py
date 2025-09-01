#!/usr/bin/env python3
"""
AI检测器集成脚本
将AI异常检测器集成到现有的DPU系统中
"""

import os
import sys
import json
import logging
import time
import threading
from typing import Dict, Optional, List
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_engine.inference.ai_anomaly_detector import AIAnomalyDetector, AIAnomalyResult
from src.ai_engine.inference.predictive_analyzer import PredictiveAnalyzer
from anomaly_detector import AnomalyDetector
from telemetry_simulator import TelemetrySimulator
from defense_controller import DefenseController

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HybridAnomalyDetector:
    """混合异常检测器 - 结合规则检测和AI检测"""
    
    def __init__(self, ai_model_path: str = None, config_path: str = None):
        # 初始化规则检测器
        self.rule_detector = AnomalyDetector()
        
        # 初始化AI检测器
        if ai_model_path and os.path.exists(ai_model_path):
            self.ai_detector = AIAnomalyDetector(model_path=ai_model_path, config_path=config_path)
            self.ai_model_loaded = True
        else:
            self.ai_detector = None
            self.ai_model_loaded = False
            logger.warning("AI model not loaded, using rule-based detection only")
        
        # 初始化预测性分析器
        self.predictive_analyzer = PredictiveAnalyzer(model_path=ai_model_path)
        
        # 检测模式: 'rule_only', 'ai_only', 'hybrid'
        self.detection_mode = 'hybrid'
        
        # 权重配置
        self.rule_weight = 0.3
        self.ai_weight = 0.7
        
        # 检测历史
        self.detection_history = []
        
        logger.info(f"Hybrid Anomaly Detector initialized with mode: {self.detection_mode}")
        logger.info(f"AI model loaded: {self.ai_model_loaded}")
    
    def detect_anomaly(self, metrics: Dict, defense_controller=None) -> Dict:
        """
        混合异常检测
        Args:
            metrics: 网络指标
            defense_controller: 防御控制器
        Returns:
            检测结果
        """
        # 添加数据到预测性分析器
        self.predictive_analyzer.add_metrics(metrics)
        
        if self.detection_mode == 'rule_only':
            return self._rule_detection(metrics, defense_controller)
        elif self.detection_mode == 'ai_only':
            return self._ai_detection(metrics, defense_controller)
        else:  # hybrid
            return self._hybrid_detection(metrics, defense_controller)
    
    def _rule_detection(self, metrics: Dict, defense_controller=None) -> Dict:
        """规则检测"""
        result = self.rule_detector.detect_anomaly(metrics, defense_controller)
        return {
            'risk_score': result['risk_score'],
            'is_anomaly': result['is_anomaly'],
            'anomaly_type': result['anomaly_type'],
            'confidence': result['confidence'],
            'detection_method': 'rule_based',
            'timestamp': int(time.time())
        }
    
    def _ai_detection(self, metrics: Dict, defense_controller=None) -> Dict:
        """AI检测"""
        result = self.ai_detector.detect_anomaly(metrics, defense_controller)
        return {
            'risk_score': result.risk_score,
            'is_anomaly': result.is_anomaly,
            'anomaly_type': result.anomaly_type,
            'confidence': result.confidence,
            'prediction_score': result.prediction_score,
            'detection_method': 'ai_based',
            'model_version': result.model_version,
            'timestamp': result.timestamp
        }
    
    def _hybrid_detection(self, metrics: Dict, defense_controller=None) -> Dict:
        """混合检测"""
        # 规则检测
        rule_result = self._rule_detection(metrics, defense_controller)
        
        # AI检测
        ai_result = self._ai_detection(metrics, defense_controller)
        
        # 加权融合
        hybrid_risk_score = (
            rule_result['risk_score'] * self.rule_weight +
            ai_result['risk_score'] * self.ai_weight
        )
        
        # 判断异常
        hybrid_is_anomaly = hybrid_risk_score > 70
        
        # 选择异常类型（优先AI检测结果）
        anomaly_type = ai_result['anomaly_type'] if ai_result['anomaly_type'] != 'unknown' else rule_result['anomaly_type']
        
        # 计算综合置信度
        hybrid_confidence = (
            rule_result['confidence'] * self.rule_weight +
            ai_result['confidence'] * self.ai_weight
        )
        
        result = {
            'risk_score': hybrid_risk_score,
            'is_anomaly': hybrid_is_anomaly,
            'anomaly_type': anomaly_type,
            'confidence': hybrid_confidence,
            'detection_method': 'hybrid',
            'rule_score': rule_result['risk_score'],
            'ai_score': ai_result['risk_score'],
            'ai_prediction': ai_result['prediction_score'],
            'model_version': ai_result.get('model_version', 'unknown'),
            'timestamp': int(time.time())
        }
        
        # 添加到历史记录
        self.detection_history.append(result)
        if len(self.detection_history) > 100:
            self.detection_history.pop(0)
        
        return result
    
    def set_detection_mode(self, mode: str):
        """设置检测模式"""
        if mode in ['rule_only', 'ai_only', 'hybrid']:
            self.detection_mode = mode
            logger.info(f"Detection mode changed to: {mode}")
        else:
            logger.error(f"Invalid detection mode: {mode}")
    
    def set_weights(self, rule_weight: float, ai_weight: float):
        """设置权重"""
        if abs(rule_weight + ai_weight - 1.0) < 0.01:  # 允许小的浮点误差
            self.rule_weight = rule_weight
            self.ai_weight = ai_weight
            logger.info(f"Weights updated: rule={rule_weight}, ai={ai_weight}")
        else:
            logger.error("Weights must sum to 1.0")
    
    def get_detection_history(self, window_size: int = 50) -> list:
        """获取检测历史"""
        history = self.detection_history[-window_size:]
        # 修复JSON序列化问题：将numpy类型转换为Python原生类型
        serializable_history = []
        for record in history:
            serializable_record = {}
            for key, value in record.items():
                if hasattr(value, 'item'):  # numpy类型
                    serializable_record[key] = value.item()
                else:
                    serializable_record[key] = value
            serializable_history.append(serializable_record)
        return serializable_history
    
    def get_status(self) -> Dict:
        """获取检测器状态"""
        return {
            'detection_mode': self.detection_mode,
            'rule_weight': self.rule_weight,
            'ai_weight': self.ai_weight,
            'ai_model_loaded': self.ai_model_loaded,
            'ai_model_version': self.ai_detector.model_version if self.ai_model_loaded else 'unknown',
            'history_size': len(self.detection_history)
        }
    
    def get_prediction_data(self, hours: int = 24) -> Dict:
        """获取预测数据"""
        return self.predictive_analyzer.predict_attack_probability(hours)
    
    def get_attack_timeline(self, hours: int = 24) -> Dict:
        """获取攻击时间线"""
        return self.predictive_analyzer.get_attack_timeline(hours)
    
    def get_risk_heatmap(self, hours: int = 24) -> Dict:
        """获取风险热力图"""
        return self.predictive_analyzer.get_risk_heatmap(hours)
    
    def get_prediction_insights(self) -> Dict:
        """获取预测洞察"""
        return self.predictive_analyzer.get_prediction_insights()

def integrate_with_existing_system():
    """集成到现有系统"""
    logger.info("开始集成AI检测器到现有系统...")
    
    # 检查模型文件
    model_path = "models/anomaly_lstm.pth"
    if not os.path.exists(model_path):
        logger.warning(f"AI模型文件不存在: {model_path}")
        logger.info("将使用规则检测模式")
        model_path = None
    
    # 创建混合检测器
    hybrid_detector = HybridAnomalyDetector(ai_model_path=model_path)
    
    # 创建模拟器和防御控制器
    simulator = TelemetrySimulator()
    defense_controller = DefenseController(simulator=simulator)
    simulator.set_defense_controller(defense_controller)
    
    # 测试集成
    logger.info("测试集成系统...")
    
    # 测试正常数据
    normal_metrics = simulator.get_metrics()
    normal_result = hybrid_detector.detect_anomaly(normal_metrics, defense_controller)
    logger.info(f"正常数据检测结果: {normal_result}")
    
    # 测试异常数据
    simulator.trigger_anomaly('ddos_attack')
    time.sleep(2)
    anomaly_metrics = simulator.get_metrics()
    anomaly_result = hybrid_detector.detect_anomaly(anomaly_metrics, defense_controller)
    logger.info(f"异常数据检测结果: {anomaly_result}")
    
    # 重置模拟器
    simulator.reset_anomaly()
    
    return hybrid_detector, simulator, defense_controller

def create_integration_api():
    """创建集成API"""
    api_code = '''
# 在app.py中添加以下API端点

@app.route('/api/ai/status')
def get_ai_status():
    """获取AI检测器状态"""
    global hybrid_detector
    if hybrid_detector:
        return jsonify(hybrid_detector.get_status())
    return jsonify({'error': 'AI detector not initialized'})

@app.route('/api/ai/mode', methods=['POST'])
def set_ai_mode():
    """设置AI检测模式"""
    global hybrid_detector
    if hybrid_detector:
        data = request.get_json()
        mode = data.get('mode', 'hybrid')
        hybrid_detector.set_detection_mode(mode)
        return jsonify({'success': True, 'mode': mode})
    return jsonify({'error': 'AI detector not initialized'})

@app.route('/api/ai/weights', methods=['POST'])
def set_ai_weights():
    """设置AI检测权重"""
    global hybrid_detector
    if hybrid_detector:
        data = request.get_json()
        rule_weight = data.get('rule_weight', 0.3)
        ai_weight = data.get('ai_weight', 0.7)
        hybrid_detector.set_weights(rule_weight, ai_weight)
        return jsonify({'success': True, 'rule_weight': rule_weight, 'ai_weight': ai_weight})
    return jsonify({'error': 'AI detector not initialized'})

@app.route('/api/ai/history')
def get_ai_history():
    """获取AI检测历史"""
    global hybrid_detector
    if hybrid_detector:
        window_size = request.args.get('window_size', 50, type=int)
        history = hybrid_detector.get_detection_history(window_size)
        return jsonify({'history': history})
    return jsonify({'error': 'AI detector not initialized'})
'''
    
    with open('integration_api.py', 'w') as f:
        f.write(api_code)
    
    logger.info("集成API代码已保存到: integration_api.py")

def create_web_interface_updates():
    """创建Web界面更新"""
    dashboard_updates = '''
<!-- 在dashboard.html中添加AI检测器控制面板 -->

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
        <input type="range" id="ruleWeight" min="0" max="1" step="0.1" value="0.3" onchange="setWeights()">
        <span id="ruleWeightValue">0.3</span>
    </div>
    
    <div class="control-group">
        <label>AI权重:</label>
        <input type="range" id="aiWeight" min="0" max="1" step="0.1" value="0.7" onchange="setWeights()">
        <span id="aiWeightValue">0.7</span>
    </div>
    
    <div class="ai-status">
        <h4>AI模型状态</h4>
        <div id="aiModelStatus">加载中...</div>
    </div>
</div>

<script>
// AI检测器控制函数
function setDetectionMode() {
    const mode = document.getElementById('detectionMode').value;
    fetch('/api/ai/mode', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mode: mode})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Detection mode updated:', data.mode);
        }
    });
}

function setWeights() {
    const ruleWeight = parseFloat(document.getElementById('ruleWeight').value);
    const aiWeight = parseFloat(document.getElementById('aiWeight').value);
    
    document.getElementById('ruleWeightValue').textContent = ruleWeight.toFixed(1);
    document.getElementById('aiWeightValue').textContent = aiWeight.toFixed(1);
    
    fetch('/api/ai/weights', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({rule_weight: ruleWeight, ai_weight: aiWeight})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Weights updated');
        }
    });
}

function updateAIStatus() {
    fetch('/api/ai/status')
    .then(response => response.json())
    .then(data => {
        const statusDiv = document.getElementById('aiModelStatus');
        if (data.ai_model_loaded) {
            statusDiv.innerHTML = `
                <p>✅ 模型已加载</p>
                <p>版本: ${data.ai_model_version}</p>
                <p>模式: ${data.detection_mode}</p>
                <p>历史记录: ${data.history_size}</p>
            `;
        } else {
            statusDiv.innerHTML = '<p>❌ 模型未加载</p>';
        }
    });
}

// 定期更新AI状态
setInterval(updateAIStatus, 5000);
updateAIStatus();
</script>
'''
    
    with open('dashboard_ai_updates.html', 'w') as f:
        f.write(dashboard_updates)
    
    logger.info("Web界面更新代码已保存到: dashboard_ai_updates.html")

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("AI检测器集成脚本")
    logger.info("=" * 60)
    
    # 集成到现有系统
    hybrid_detector, simulator, defense_controller = integrate_with_existing_system()
    
    # 创建集成API
    create_integration_api()
    
    # 创建Web界面更新
    create_web_interface_updates()
    
    # 创建使用说明
    usage_guide = {
        'integration_steps': [
            '1. 运行 train_ai_model.py 训练AI模型',
            '2. 运行此脚本集成AI检测器',
            '3. 将integration_api.py中的代码添加到app.py',
            '4. 将dashboard_ai_updates.html中的代码添加到dashboard.html',
            '5. 重启应用服务器'
        ],
        'api_endpoints': [
            'GET /api/ai/status - 获取AI检测器状态',
            'POST /api/ai/mode - 设置检测模式',
            'POST /api/ai/weights - 设置检测权重',
            'GET /api/ai/history - 获取检测历史'
        ],
        'detection_modes': {
            'hybrid': '混合模式：结合规则检测和AI检测',
            'rule_only': '仅规则检测：使用原有的规则检测',
            'ai_only': '仅AI检测：仅使用AI模型检测'
        },
        'configuration': {
            'model_path': 'models/anomaly_lstm.pth',
            'config_path': 'configs/ai_model_config.json',
            'default_weights': {'rule': 0.3, 'ai': 0.7}
        }
    }
    
    with open('ai_integration_guide.json', 'w') as f:
        json.dump(usage_guide, f, indent=2)
    
    logger.info("=" * 60)
    logger.info("AI检测器集成完成!")
    logger.info("=" * 60)
    logger.info("请查看以下文件:")
    logger.info("- integration_api.py: API集成代码")
    logger.info("- dashboard_ai_updates.html: Web界面更新")
    logger.info("- ai_integration_guide.json: 使用说明")
    logger.info("=" * 60)

if __name__ == "__main__":
    main() 