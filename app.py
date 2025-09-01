#!/usr/bin/env python3


from flask import Flask, render_template, jsonify, request
from telemetry_simulator import TelemetrySimulator
from anomaly_detector import AnomalyDetector
from defense_controller import DefenseController
from integrate_ai_detector import HybridAnomalyDetector
import threading
import time
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 全局组件
telemetry_simulator = None
anomaly_detector = None
defense_controller = None
simulation_thread = None
running = False

# 全局数据存储
current_metrics = {}
current_risk_score = 0
current_alerts = []
system_status = "normal"

# 新增：全局变量
hybrid_detector = None

# 初始化组件
def initialize_components():
    """初始化所有组件"""
    global telemetry_simulator, anomaly_detector, defense_controller
    
    logger.info("初始化系统组件...")
    
    # 初始化数据模拟器
    telemetry_simulator = TelemetrySimulator()
    
    # 初始化异常检测器
    anomaly_detector = AnomalyDetector()
    
    # 初始化防御控制器，传入模拟器
    defense_controller = DefenseController(simulator=telemetry_simulator)
    
    # 新增：设置模拟器的防御控制器引用
    telemetry_simulator.set_defense_controller(defense_controller)
    
    logger.info("所有组件初始化完成")

# 立即初始化组件
initialize_components()

# 3. 初始化AI检测器
def initialize_ai_detector():
    global hybrid_detector
    model_path = "models/anomaly_lstm.pth"
    config_path = "configs/ai_model_config.json"
    hybrid_detector = HybridAnomalyDetector(ai_model_path=model_path, config_path=config_path)

initialize_ai_detector()

@app.route('/')
def dashboard():
    """主仪表板页面"""
    return render_template('dashboard.html')

@app.route('/test')
def test():
    """测试页面"""
    return render_template('test.html')

@app.route('/api/metrics')
def get_metrics():
    """获取当前指标数据"""
    global current_metrics, current_risk_score, system_status
    return jsonify({
        'metrics': current_metrics,
        'risk_score': current_risk_score,
        'status': system_status,
        'timestamp': int(time.time())
    })

@app.route('/api/alerts')
def get_alerts():
    """获取告警信息"""
    global current_alerts
    return jsonify({
        'alerts': current_alerts,
        'count': len(current_alerts)
    })

@app.route('/api/defense/status')
def get_defense_status():
    """获取防御状态"""
    global defense_controller
    if defense_controller:
        status = defense_controller.get_status()
        # 添加防御模式信息
        status['mode'] = defense_controller.mode
        return jsonify(status)
    return jsonify({'active': False, 'rules': [], 'mode': 'auto'})

@app.route('/api/defense/trigger', methods=['POST'])
def trigger_defense():
    """手动触发防御"""
    global defense_controller
    if defense_controller:
        data = request.get_json()
        risk_score = data.get('risk_score', 0)
        anomaly_type = data.get('anomaly_type', None)
        defense_controller.trigger_defense(risk_score, anomaly_type)
        return jsonify({'success': True, 'message': '防御已触发'})
    return jsonify({'success': False, 'message': '防御控制器未初始化'})

@app.route('/api/defense/mode', methods=['POST'])
def set_defense_mode():
    """设置防御模式"""
    global defense_controller
    if defense_controller:
        data = request.get_json()
        mode = data.get('mode', 'auto')
        if mode in ['auto', 'manual']:
            defense_controller.set_mode(mode)
            return jsonify({'success': True, 'message': f'防御模式已切换为: {mode}'})
        else:
            return jsonify({'success': False, 'message': '无效的防御模式'})
    return jsonify({'success': False, 'message': '防御控制器未初始化'})

@app.route('/api/defense/manual', methods=['POST'])
def manual_defense():
    """手动触发防御"""
    global defense_controller, current_risk_score
    if defense_controller:
        data = request.get_json()
        risk_score = data.get('risk_score', current_risk_score)
        anomaly_type = data.get('anomaly_type', None)
        success = defense_controller.manual_trigger(risk_score, anomaly_type)
        if success:
            return jsonify({'success': True, 'message': '手动防御已触发'})
        else:
            return jsonify({'success': False, 'message': '手动防御触发失败'})
    return jsonify({'success': False, 'message': '防御控制器未初始化'})

# 新增：关闭防御API
@app.route('/api/defense/disable', methods=['POST'])
def disable_defense():
    """关闭防御"""
    global defense_controller
    if defense_controller:
        success = defense_controller.disable_defense()
        if success:
            return jsonify({'success': True, 'message': '防御系统已关闭'})
        else:
            return jsonify({'success': False, 'message': '关闭防御失败'})
    return jsonify({'success': False, 'message': '防御控制器未初始化'})

@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """启动模拟"""
    global running, simulation_thread
    if not running:
        running = True
        simulation_thread = threading.Thread(target=simulation_loop)
        simulation_thread.daemon = True
        simulation_thread.start()
        return jsonify({'success': True, 'message': '模拟已启动'})
    return jsonify({'success': False, 'message': '模拟已在运行'})

@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """停止模拟"""
    global running
    running = False
    return jsonify({'success': True, 'message': '模拟已停止'})

@app.route('/api/simulation/anomaly', methods=['POST'])
def trigger_anomaly():
    """触发异常场景"""
    global telemetry_simulator
    if telemetry_simulator:
        data = request.get_json()
        anomaly_type = data.get('type', 'random')
        telemetry_simulator.trigger_anomaly(anomaly_type)
        return jsonify({'success': True, 'message': f'异常场景 {anomaly_type} 已触发'})
    return jsonify({'success': False, 'message': '模拟器未初始化'})

@app.route('/api/ai/status')
def get_ai_status():
    global hybrid_detector
    if hybrid_detector:
        return jsonify(hybrid_detector.get_status())
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

@app.route('/api/prediction/attack-probability')
def get_attack_prediction():
    """获取攻击概率预测"""
    global hybrid_detector
    if hybrid_detector:
        hours = request.args.get('hours', 24, type=int)
        prediction = hybrid_detector.get_prediction_data(hours)
        return jsonify(prediction)
    return jsonify({'error': 'Predictive analyzer not initialized'})

@app.route('/api/prediction/timeline')
def get_attack_timeline():
    """获取攻击时间线"""
    global hybrid_detector
    if hybrid_detector:
        hours = request.args.get('hours', 24, type=int)
        timeline = hybrid_detector.get_attack_timeline(hours)
        return jsonify(timeline)
    return jsonify({'error': 'Predictive analyzer not initialized'})

@app.route('/api/prediction/heatmap')
def get_risk_heatmap():
    """获取风险热力图"""
    global hybrid_detector
    if hybrid_detector:
        hours = request.args.get('hours', 24, type=int)
        heatmap = hybrid_detector.get_risk_heatmap(hours)
        return jsonify(heatmap)
    return jsonify({'error': 'Predictive analyzer not initialized'})

@app.route('/api/prediction/insights')
def get_prediction_insights():
    """获取预测洞察"""
    global hybrid_detector
    if hybrid_detector:
        insights = hybrid_detector.get_prediction_insights()
        return jsonify(insights)
    return jsonify({'error': 'Predictive analyzer not initialized'})

@app.route('/api/alerts/test', methods=['POST'])
def add_test_alert():
    """添加测试告警"""
    global current_alerts
    
    try:
        data = request.get_json()
        alert_types = ['normal', 'ddos_attack', 'resource_exhaustion', 'packet_loss', 'suspicious_behavior', 
                      'low_risk_anomaly', 'medium_risk_anomaly', 'high_risk_anomaly', 'critical_anomaly']
        
        alert_type = data.get('type', 'medium_risk_anomaly')
        risk_scores = {
            'normal': 15.0,
            'ddos_attack': 95.0,
            'resource_exhaustion': 85.0,
            'packet_loss': 75.0,
            'suspicious_behavior': 65.0,
            'critical_anomaly': 95.0,
            'high_risk_anomaly': 85.0,
            'medium_risk_anomaly': 65.0,
            'low_risk_anomaly': 45.0
        }
        
        messages = {
            'normal': '系统运行正常，所有指标正常',
            'ddos_attack': '检测到DDoS攻击，流量异常增长',
            'resource_exhaustion': '系统资源耗尽，CPU/内存使用率过高',
            'packet_loss': '检测到严重丢包，网络连接不稳定',
            'suspicious_behavior': '检测到可疑行为，加密流量异常',
            'critical_anomaly': '检测到严重异常，需要立即处理',
            'high_risk_anomaly': '检测到高风险异常',
            'medium_risk_anomaly': '检测到中等风险异常',
            'low_risk_anomaly': '检测到低风险异常'
        }
        
        current_time = int(time.time())
        risk_score = risk_scores.get(alert_type, 50.0)
        message = messages.get(alert_type, f'检测到异常: {alert_type}')
        
        alert = {
            'timestamp': current_time,
            'type': alert_type,
            'risk_score': risk_score,
            'message': f"{message}, 风险评分: {risk_score:.1f}"
        }
        
        current_alerts.append(alert)
        
        # 保持最近10条告警
        if len(current_alerts) > 10:
            current_alerts = current_alerts[-10:]
        
        logger.info(f"添加测试告警: {alert_type}, 风险评分: {risk_score}")
        
        return jsonify({
            'success': True, 
            'message': f'测试告警已添加: {alert_type}',
            'alert': alert
        })
        
    except Exception as e:
        logger.error(f"添加测试告警失败: {e}")
        return jsonify({'success': False, 'message': f'添加测试告警失败: {str(e)}'})

def simulation_loop():
    """模拟循环"""
    global running, current_metrics, current_risk_score, current_alerts, system_status
    
    logger.info("模拟循环已启动")
    
    while running:
        try:
            # 获取模拟数据
            metrics = telemetry_simulator.get_metrics()
            current_metrics = metrics
            
            # 异常检测，传入防御控制器
            result = anomaly_detector.detect_anomaly(metrics, defense_controller=defense_controller)
            
            # 确保风险评分正确更新
            current_risk_score = float(result.get('risk_score', 0))
            
            # 更新系统状态
            if current_risk_score > 70:
                system_status = "critical"
            elif current_risk_score > 50:
                system_status = "warning"
            else:
                system_status = "normal"
            
            # 检测异常和正常状态，都要生成通知
            is_anomaly = result.get('is_anomaly', False)
            anomaly_type = result.get('anomaly_type', 'normal')
            current_time = int(time.time())
            
            if is_anomaly and anomaly_type != 'normal' and current_risk_score > 40:
                # 检查是否需要触发防御（自动模式）
                if defense_controller.mode == "auto":
                    defense_controller.trigger_defense(current_risk_score, anomaly_type)
                
                # 添加异常告警（避免重复告警）
                # 检查最近5秒内是否已有相同类型的告警
                recent_alerts = [a for a in current_alerts if current_time - a['timestamp'] < 5 and a['type'] == anomaly_type]
                
                if not recent_alerts:
                    alert = {
                        'timestamp': current_time,
                        'type': anomaly_type,
                        'risk_score': current_risk_score,
                        'message': f"检测到异常: {anomaly_type}, 风险评分: {current_risk_score:.1f}"
                    }
                    current_alerts.append(alert)
                    logger.info(f"添加异常告警: {anomaly_type}, 风险评分: {current_risk_score}")
            
            else:
                # 系统正常时，定期添加正常状态通知（每20秒一次）
                recent_normal_alerts = [a for a in current_alerts if current_time - a['timestamp'] < 20 and a['type'] == 'normal']
                
                if not recent_normal_alerts:
                    normal_alert = {
                        'timestamp': current_time,
                        'type': 'normal',
                        'risk_score': current_risk_score,
                        'message': f"系统运行正常，风险评分: {current_risk_score:.1f}"
                    }
                    current_alerts.append(normal_alert)
                    logger.info(f"添加正常状态通知: 风险评分: {current_risk_score}")
            
            # 清理超过30秒的旧告警
            current_time = int(time.time())
            current_alerts = [a for a in current_alerts if current_time - a['timestamp'] < 30]
            
            # 保持最近10条告警
            if len(current_alerts) > 10:
                current_alerts = current_alerts[-10:]
            
            # 调用AI检测器
            ai_result = hybrid_detector.detect_anomaly(metrics, defense_controller)
            
            # 等待1秒
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"模拟循环错误: {e}")
            time.sleep(1)

if __name__ == '__main__':
    # 启动Flask应用
    logger.info("启动Web服务器...")
    app.run(host='0.0.0.0', port=5002, debug=True) 