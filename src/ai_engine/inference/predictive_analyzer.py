import numpy as np
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from ..models.simple_lstm import AnomalyPredictor
from ..training.data_processor import DataProcessor

logger = logging.getLogger(__name__)

class PredictiveAnalyzer:
    """预测性分析器"""
    
    def __init__(self, model_path: str = None):
        self.predictor = AnomalyPredictor(model_path=model_path)
        self.data_processor = DataProcessor()
        self.historical_data = []
        self.prediction_cache = {}
        self.cache_duration = 300  # 5分钟缓存
        
    def add_metrics(self, metrics: Dict):
        """添加新的指标数据"""
        # 转换为numpy数组，处理来自遥测模拟器的实际数据
        metrics_array = np.array([
            float(metrics.get('cpu_usage', 0)),
            float(metrics.get('memory_usage', 0)),
            float(metrics.get('bytes_per_sec', 0)) / 1000000.0,  # 网络吞吐量，转换为MB/s
            float(metrics.get('dropped_packets', 0)),  # 丢包率
            float(metrics.get('error_count', 0)),  # 延迟/错误
            float(metrics.get('active_connections', 0)),  # 连接数
            float(metrics.get('error_count', 0)) / max(1, float(metrics.get('packets_per_sec', 1))),  # 错误率
            float(metrics.get('bytes_per_sec', 0)) / 1000000.0,  # 带宽利用率
            float(metrics.get('active_connections', 0))  # 活跃连接数
        ])
        
        # 添加时间戳
        current_time = time.time()
        data_point = {
            'timestamp': current_time,
            'metrics': metrics_array,
            'raw_metrics': metrics.copy()  # 保存原始数据用于调试
        }
        
        self.historical_data.append(data_point)
        
        # 保持最近1000个数据点
        if len(self.historical_data) > 1000:
            self.historical_data = self.historical_data[-1000:]
        
        # 清除缓存
        self.prediction_cache.clear()
        
        # 记录数据添加日志
        logger.debug(f"Added metrics data point: {len(self.historical_data)} total points")
    
    def get_historical_metrics_for_prediction(self):
        """获取用于预测的历史指标数据"""
        if len(self.historical_data) < 10:
            return None
        
        # 返回最近的指标数据
        return [point['metrics'] for point in self.historical_data[-100:]]
    
    def predict_attack_probability(self, hours: int = 24) -> Dict:
        """预测未来攻击概率"""
        cache_key = f"prediction_{hours}"
        
        # 检查缓存
        if cache_key in self.prediction_cache:
            cache_time, cache_data = self.prediction_cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                return cache_data
        
        if len(self.historical_data) < 10:
            return {
                "error": "Insufficient historical data",
                "min_required": 10,
                "available": len(self.historical_data)
            }
        
        try:
            # 获取历史指标数据用于预测
            historical_metrics = self.get_historical_metrics_for_prediction()
            
            # 获取预测结果
            prediction_result = self.predictor.predict_future_anomalies(
                historical_metrics, hours
            )
            
            # 添加时间戳和元数据
            result = {
                "timestamp": int(time.time()),
                "prediction_hours": hours,
                "data_points_used": len(self.historical_data),
                "predictions": prediction_result['predictions'],
                "confidence": prediction_result['confidence'],
                "trend": prediction_result['trend'],
                "summary": self._generate_summary(prediction_result['predictions'])
            }
            
            # 缓存结果
            self.prediction_cache[cache_key] = (time.time(), result)
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                "error": f"Prediction failed: {str(e)}",
                "timestamp": int(time.time())
            }
    
    def get_attack_timeline(self, hours: int = 24) -> Dict:
        """获取攻击时间线"""
        prediction = self.predict_attack_probability(hours)
        
        if "error" in prediction:
            return prediction
        
        timeline = {
            "current_time": datetime.now().isoformat(),
            "prediction_period": f"{hours} hours",
            "high_risk_periods": [],
            "medium_risk_periods": [],
            "low_risk_periods": [],
            "trend_analysis": prediction['trend']
        }
        
        for pred in prediction['predictions']:
            timestamp = datetime.fromtimestamp(pred['timestamp'])
            period = {
                "hour": pred['hour'],
                "timestamp": timestamp.isoformat(),
                "probability": pred['anomaly_probability'],
                "risk_level": pred['risk_level']
            }
            
            if pred['risk_level'] == 'high':
                timeline['high_risk_periods'].append(period)
            elif pred['risk_level'] == 'medium':
                timeline['medium_risk_periods'].append(period)
            else:
                timeline['low_risk_periods'].append(period)
        
        return timeline
    
    def get_risk_heatmap(self, hours: int = 24) -> Dict:
        """获取风险热力图数据"""
        prediction = self.predict_attack_probability(hours)
        
        if "error" in prediction:
            return prediction
        
        heatmap_data = []
        for pred in prediction['predictions']:
            heatmap_data.append({
                "hour": pred['hour'],
                "probability": pred['anomaly_probability'],
                "risk_level": pred['risk_level'],
                "timestamp": pred['timestamp']
            })
        
        return {
            "heatmap_data": heatmap_data,
            "max_probability": max([p['probability'] for p in heatmap_data]),
            "min_probability": min([p['probability'] for p in heatmap_data]),
            "average_probability": np.mean([p['probability'] for p in heatmap_data])
        }
    
    def get_prediction_insights(self) -> Dict:
        """获取预测洞察"""
        prediction_24h = self.predict_attack_probability(24)
        prediction_6h = self.predict_attack_probability(6)
        
        if "error" in prediction_24h:
            return {"error": prediction_24h["error"]}
        
        insights = {
            "timestamp": int(time.time()),
            "short_term_risk": self._analyze_short_term_risk(prediction_6h),
            "long_term_trend": self._analyze_long_term_trend(prediction_24h),
            "recommendations": self._generate_recommendations(prediction_24h),
            "confidence_level": prediction_24h['confidence']
        }
        
        return insights
    
    def _generate_summary(self, predictions: List[Dict]) -> Dict:
        """生成预测摘要"""
        if not predictions:
            return {}
        
        probabilities = [p['anomaly_probability'] for p in predictions]
        risk_levels = [p['risk_level'] for p in predictions]
        
        high_risk_count = risk_levels.count('high')
        medium_risk_count = risk_levels.count('medium')
        low_risk_count = risk_levels.count('low')
        
        return {
            "max_probability": max(probabilities),
            "min_probability": min(probabilities),
            "average_probability": np.mean(probabilities),
            "high_risk_hours": high_risk_count,
            "medium_risk_hours": medium_risk_count,
            "low_risk_hours": low_risk_count,
            "peak_risk_hour": predictions[np.argmax(probabilities)]['hour']
        }
    
    def _analyze_short_term_risk(self, prediction: Dict) -> Dict:
        """分析短期风险"""
        if "error" in prediction:
            return {"error": prediction["error"]}
        
        next_6_hours = prediction['predictions'][:6]
        high_risk_hours = [p for p in next_6_hours if p['risk_level'] == 'high']
        
        return {
            "immediate_risk": len(high_risk_hours) > 0,
            "high_risk_hours": len(high_risk_hours),
            "max_short_term_probability": max([p['anomaly_probability'] for p in next_6_hours]),
            "recommendation": "Increase monitoring" if len(high_risk_hours) > 0 else "Normal operations"
        }
    
    def _analyze_long_term_trend(self, prediction: Dict) -> Dict:
        """分析长期趋势"""
        if "error" in prediction:
            return {"error": prediction["error"]}
        
        trend = prediction['trend']
        
        return {
            "trend_direction": trend['direction'],
            "trend_strength": abs(trend.get('slope', 0)),
            "trend_description": self._describe_trend(trend),
            "forecast_reliability": prediction['confidence']
        }
    
    def _describe_trend(self, trend: Dict) -> str:
        """描述趋势"""
        direction = trend['direction']
        slope = abs(trend.get('slope', 0))
        
        if direction == 'up':
            if slope > 0.05:
                return "Strong upward trend - high risk increasing"
            else:
                return "Moderate upward trend - risk gradually increasing"
        elif direction == 'down':
            if slope > 0.05:
                return "Strong downward trend - risk decreasing"
            else:
                return "Moderate downward trend - risk gradually decreasing"
        else:
            return "Stable trend - risk level consistent"
    
    def _generate_recommendations(self, prediction: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if "error" in prediction:
            return ["Collect more historical data for accurate predictions"]
        
        summary = prediction['summary']
        trend = prediction['trend']
        
        # 基于风险等级的建议
        if summary['high_risk_hours'] > 5:
            recommendations.append("High risk period detected - activate enhanced monitoring")
        
        if summary['max_probability'] > 0.8:
            recommendations.append("Extreme risk predicted - prepare incident response team")
        
        # 基于趋势的建议
        if trend['direction'] == 'up':
            recommendations.append("Risk trend increasing - review security measures")
        elif trend['direction'] == 'down':
            recommendations.append("Risk trend decreasing - maintain current security posture")
        
        # 基于置信度的建议
        if prediction['confidence'] < 0.6:
            recommendations.append("Low prediction confidence - consider manual review")
        
        if not recommendations:
            recommendations.append("Normal operations - continue routine monitoring")
        
        return recommendations
    
    def get_status(self) -> Dict:
        """获取分析器状态"""
        return {
            "historical_data_points": len(self.historical_data),
            "prediction_cache_size": len(self.prediction_cache),
            "model_loaded": hasattr(self.predictor, 'model'),
            "last_prediction_time": max([t for t, _ in self.prediction_cache.values()]) if self.prediction_cache else None
        } 