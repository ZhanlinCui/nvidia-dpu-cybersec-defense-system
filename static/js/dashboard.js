// 仪表板JavaScript功能
class Dashboard {
    constructor() {
        this.chart = null;
        this.updateInterval = null;
        this.isRunning = false;
        this.chartData = {
            labels: [],
            datasets: [{
                label: '风险评分',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4
            }, {
                label: '数据包/秒',
                data: [],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4,
                yAxisID: 'y1'
            }]
        };
        
        this.init();
    }
    
    init() {
        this.initChart();
        this.bindEvents();
        this.startUpdates();
    }
    
    initChart() {
        const ctx = document.getElementById('metricsChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: this.chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: '时间'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: '风险评分'
                        },
                        min: 0,
                        max: 100
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: '数据包/秒'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
    
    bindEvents() {
        // 启动模拟
        document.getElementById('startSimulation').addEventListener('click', () => {
            this.startSimulation();
        });
        
        // 停止模拟
        document.getElementById('stopSimulation').addEventListener('click', () => {
            this.stopSimulation();
        });
        
        // 触发DDoS
        document.getElementById('triggerDDoS').addEventListener('click', () => {
            this.triggerAnomaly('ddos');
        });
        
        // 触发资源耗尽
        document.getElementById('triggerResource').addEventListener('click', () => {
            this.triggerAnomaly('resource_exhaustion');
        });

        // 新增：防御模式切换
        document.getElementById('autoMode').addEventListener('click', () => {
            this.setDefenseMode('auto');
        });
        
        document.getElementById('manualMode').addEventListener('click', () => {
            this.setDefenseMode('manual');
        });

        // 新增：手动触发防御
        document.getElementById('manualDefense').addEventListener('click', () => {
            this.triggerManualDefense();
        });

        // 新增：关闭防御
        document.getElementById('disableDefense').addEventListener('click', () => {
            this.disableDefense();
        });
    }
    
    startUpdates() {
        this.updateInterval = setInterval(() => {
            this.updateMetrics();
        }, 1000);
    }
    
    async updateMetrics() {
        try {
            const response = await fetch('/api/metrics');
            const data = await response.json();
            
            this.updateDashboard(data);
            this.updateChart(data);
            
        } catch (error) {
            console.error('更新指标失败:', error);
        }
    }
    
    updateDashboard(data) {
        const metrics = data.metrics || {};
        const riskScore = data.risk_score || 0;
        const status = data.status || 'normal';
        
        // 更新风险评分
        this.updateValue('riskScore', riskScore.toFixed(1));
        this.updateProgress('riskProgress', riskScore);
        
        // 更新系统状态
        this.updateSystemStatus(status);
        
        // 更新网络指标
        if (metrics) {
            this.updateValue('packetsPerSec', metrics.packets_per_sec || 0);
            this.updateValue('activeConnections', metrics.active_connections || 0);
            this.updateValue('bytesPerSec', this.formatBytes(metrics.bytes_per_sec || 0));
            this.updateValue('droppedPackets', metrics.dropped_packets || 0);
            this.updateValue('encryptionHits', metrics.encryption_hits || 0);
            this.updateValue('cpuUsage', (metrics.cpu_usage || 0).toFixed(1) + '%');
            this.updateValue('memoryUsage', (metrics.memory_usage || 0).toFixed(1) + '%');
            this.updateValue('errorCount', metrics.error_count || 0);
        }
        
        // 更新防御状态
        this.updateDefenseStatus();
    }
    
    updateValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            const oldValue = element.textContent;
            element.textContent = value;
            
            // 添加数值变化动画
            if (oldValue !== value) {
                element.classList.add('value-change');
                setTimeout(() => {
                    element.classList.remove('value-change');
                }, 500);
            }
        }
    }
    
    updateProgress(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.width = value + '%';
            
            // 根据值更新颜色
            if (value > 80) {
                element.className = 'progress-bar bg-danger';
            } else if (value > 50) {
                element.className = 'progress-bar bg-warning';
            } else {
                element.className = 'progress-bar bg-success';
            }
        }
    }
    
    updateSystemStatus(status) {
        const statusElement = document.getElementById('systemStatus');
        const indicatorElement = document.getElementById('statusIndicator');
        
        if (statusElement && indicatorElement) {
            // 移除所有状态类
            statusElement.classList.remove('status-normal', 'status-warning', 'status-critical');
            indicatorElement.classList.remove('normal', 'warning', 'critical');
            
            // 添加新状态类
            if (status === 'critical') {
                statusElement.classList.add('status-critical');
                indicatorElement.classList.add('critical');
                statusElement.textContent = '严重';
            } else if (status === 'warning') {
                statusElement.classList.add('status-warning');
                indicatorElement.classList.add('warning');
                statusElement.textContent = '警告';
            } else {
                statusElement.classList.add('status-normal');
                indicatorElement.classList.add('normal');
                statusElement.textContent = '正常';
            }
        }
    }
    
    async updateDefenseStatus() {
        try {
            const response = await fetch('/api/defense/status');
            const data = await response.json();
            
            if (data) {
                // 更新防御状态
                const statusText = data.active ? '已激活' : '未激活';
                const statusClass = data.active ? 'text-success' : 'text-muted';
                document.getElementById('defenseActive').textContent = statusText;
                document.getElementById('defenseActive').className = statusClass;
                
                // 更新活跃规则数
                this.updateValue('activeRules', data.active_rules_count || 0);
                
                // 更新最后触发时间
                if (data.last_trigger_time) {
                    const time = new Date(data.last_trigger_time * 1000).toLocaleTimeString();
                    this.updateValue('lastTrigger', time);
                } else {
                    this.updateValue('lastTrigger', '-');
                }
                
                // 更新防御效果
                if (data.stats && data.stats.total_triggers > 0) {
                    const effectiveness = (data.stats.successful_defenses / data.stats.total_triggers * 100).toFixed(1);
                    this.updateValue('defenseEffectiveness', effectiveness + '%');
                } else {
                    this.updateValue('defenseEffectiveness', '0%');
                }

                // 新增：更新防御模式显示
                if (data.mode) {
                    this.updateDefenseModeButtons(data.mode);
                    // 更新防御模式文本
                    const modeText = data.mode === 'auto' ? '自动' : '手动';
                    this.updateValue('defenseMode', modeText);
                }

                // 新增：更新关闭防御按钮状态
                const disableDefenseBtn = document.getElementById('disableDefense');
                if (disableDefenseBtn) {
                    disableDefenseBtn.disabled = !data.active;
                }
            }
            
        } catch (error) {
            console.error('更新防御状态失败:', error);
        }
    }
    
    updateChart(data) {
        const timestamp = new Date().toLocaleTimeString();
        const riskScore = data.risk_score || 0;
        const packetsPerSec = data.metrics ? (data.metrics.packets_per_sec || 0) : 0;
        
        // 添加新数据点
        this.chartData.labels.push(timestamp);
        this.chartData.datasets[0].data.push(riskScore);
        this.chartData.datasets[1].data.push(packetsPerSec);
        
        // 保持最近30个数据点
        if (this.chartData.labels.length > 30) {
            this.chartData.labels.shift();
            this.chartData.datasets[0].data.shift();
            this.chartData.datasets[1].data.shift();
        }
        
        // 更新图表
        if (this.chart) {
            this.chart.update('none');
        }
    }
    
    async startSimulation() {
        try {
            const response = await fetch('/api/simulation/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.isRunning = true;
                this.updateButtonStates();
                this.showNotification('模拟已启动', 'success');
                
                // 启动计时器
                if (typeof startTimers === 'function') {
                    startTimers();
                }
            }
            
        } catch (error) {
            console.error('启动模拟失败:', error);
            this.showNotification('启动模拟失败', 'error');
        }
    }
    
    async stopSimulation() {
        try {
            const response = await fetch('/api/simulation/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.isRunning = false;
                this.updateButtonStates();
                this.showNotification('模拟已停止', 'info');
                
                // 停止计时器
                if (typeof stopTimers === 'function') {
                    stopTimers();
                }
            }
            
        } catch (error) {
            console.error('停止模拟失败:', error);
            this.showNotification('停止模拟失败', 'error');
        }
    }
    
    async triggerAnomaly(type) {
        try {
            const response = await fetch('/api/simulation/anomaly', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type: type })
            });
            
            const result = await response.json();
            if (result.success) {
                this.showNotification(`异常场景 ${type} 已触发`, 'warning');
            }
            
        } catch (error) {
            console.error('触发异常失败:', error);
            this.showNotification('触发异常失败', 'error');
        }
    }
    
    updateButtonStates() {
        const startBtn = document.getElementById('startSimulation');
        const stopBtn = document.getElementById('stopSimulation');
        
        if (this.isRunning) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    }
    
    async updateAlerts() {
        try {
            const response = await fetch('/api/alerts');
            const data = await response.json();
            
            const container = document.getElementById('alertsContainer');
            
            if (data.alerts && data.alerts.length > 0) {
                // 有告警时显示告警列表
                container.innerHTML = '';
                
                // 只显示最近5个告警
                const recentAlerts = data.alerts.slice(-5);
                
                recentAlerts.forEach((alert, index) => {
                    const alertElement = this.createAlertElement(alert, index);
                    container.appendChild(alertElement);
                    
                    // 新告警添加脉冲效果
                    const currentTime = Math.floor(Date.now() / 1000);
                    if (currentTime - alert.timestamp < 10) { // 10秒内的告警
                        alertElement.classList.add('pulse');
                        // 10秒后移除脉冲效果
                        setTimeout(() => {
                            alertElement.classList.remove('pulse');
                        }, 10000 - (currentTime - alert.timestamp) * 1000);
                    }
                });
                
                // 自动滚动到最新告警
                this.scrollToLatestAlert(container);
                
                // 添加告警总数显示
                if (data.alerts.length > 5) {
                    const moreElement = document.createElement('div');
                    moreElement.className = 'alert-more text-center text-muted';
                    moreElement.innerHTML = `<small>还有 ${data.alerts.length - 5} 条更早的告警</small>`;
                    container.appendChild(moreElement);
                }
                
            } else {
                // 无告警时显示正常状态
                container.innerHTML = `
                    <div class="text-center text-success">
                        <i class="fas fa-check-circle fa-2x mb-2"></i>
                        <p class="mb-0">系统运行正常</p>
                        <small class="text-muted">暂无告警</small>
                    </div>
                `;
            }
            
        } catch (error) {
            console.error('更新告警失败:', error);
            // 错误时显示错误状态
            const container = document.getElementById('alertsContainer');
            container.innerHTML = `
                <div class="text-center text-warning">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <p class="mb-0">告警状态检查失败</p>
                    <small class="text-muted">正在重试...</small>
                </div>
            `;
        }
    }
    
    createAlertElement(alert, index = 0) {
        const div = document.createElement('div');
        div.className = `alert-item ${this.getAlertClass(alert.risk_score, alert.type)} fade-in`;
        
        // 添加堆叠延迟动画
        div.style.animationDelay = `${index * 0.1}s`;
        
        const time = new Date(alert.timestamp * 1000).toLocaleTimeString();
        const timeAgo = this.getTimeAgo(alert.timestamp);
        
        // 获取告警类型的中文描述
        const typeDescriptions = {
            'normal': '系统正常',
            'ddos_attack': 'DDoS攻击',
            'resource_exhaustion': '资源耗尽',
            'packet_loss': '数据包丢失',
            'suspicious_behavior': '可疑行为',
            'low_risk_anomaly': '低风险异常',
            'medium_risk_anomaly': '中等风险异常',
            'high_risk_anomaly': '高风险异常',
            'critical_anomaly': '严重异常'
        };
        
        const typeDisplay = typeDescriptions[alert.type] || alert.type;
        const riskLevel = this.getRiskLevel(alert.risk_score);
        
        div.innerHTML = `
            <div class="alert-header">
                <div class="alert-icon">
                    <i class="${this.getAlertIcon(alert.risk_score)}"></i>
                </div>
                <div class="alert-info">
                    <div class="alert-title">${typeDisplay}</div>
                    <div class="alert-time">${time} (${timeAgo})</div>
                </div>
                <div class="alert-risk">
                    <span class="risk-score">${alert.risk_score.toFixed(1)}</span>
                    <span class="risk-level">${riskLevel}</span>
                </div>
            </div>
            <div class="alert-message">${alert.message}</div>
        `;
        
        return div;
    }
    
    getTimeAgo(timestamp) {
        const now = Math.floor(Date.now() / 1000);
        const diff = now - timestamp;
        
        if (diff < 60) return `${diff}秒前`;
        if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
        return `${Math.floor(diff / 86400)}天前`;
    }
    
    getRiskLevel(riskScore) {
        if (riskScore >= 80) return '严重';
        if (riskScore >= 60) return '高风险';
        if (riskScore >= 40) return '中等风险';
        return '低风险';
    }
    
    getAlertIcon(riskScore) {
        if (riskScore >= 80) return 'fas fa-exclamation-triangle';
        if (riskScore >= 60) return 'fas fa-exclamation-circle';
        if (riskScore >= 40) return 'fas fa-info-circle';
        return 'fas fa-check-circle';
    }
    
    scrollToLatestAlert(container) {
        // 平滑滚动到最底部（最新告警）
        setTimeout(() => {
            container.scrollTo({
                top: container.scrollHeight,
                behavior: 'smooth'
            });
        }, 100); // 等待DOM更新完成
    }
    
    getAlertClass(riskScore, alertType = null) {
        // 正常状态始终显示为成功样式
        if (alertType === 'normal') return 'alert-success';
        
        if (riskScore >= 80) return 'alert-danger';
        if (riskScore >= 60) return 'alert-warning';
        if (riskScore >= 40) return 'alert-info';
        return 'alert-success';
    }
    
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // 新增：设置防御模式
    async setDefenseMode(mode) {
        try {
            const response = await fetch('/api/defense/mode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mode: mode })
            });
            
            const result = await response.json();
            if (result.success) {
                this.updateDefenseModeButtons(mode);
                this.showNotification(`防御模式已切换为: ${mode === 'auto' ? '自动' : '手动'}`, 'success');
            } else {
                this.showNotification(result.message, 'error');
            }
            
        } catch (error) {
            console.error('设置防御模式失败:', error);
            this.showNotification('设置防御模式失败', 'error');
        }
    }

    // 新增：更新防御模式按钮状态
    updateDefenseModeButtons(mode) {
        const autoBtn = document.getElementById('autoMode');
        const manualBtn = document.getElementById('manualMode');
        const manualDefenseBtn = document.getElementById('manualDefense');
        const disableDefenseBtn = document.getElementById('disableDefense');
        
        if (mode === 'auto') {
            autoBtn.classList.remove('btn-secondary');
            autoBtn.classList.add('btn-primary', 'active');
            manualBtn.classList.remove('btn-primary', 'active');
            manualBtn.classList.add('btn-secondary');
            manualDefenseBtn.disabled = true;
        } else {
            manualBtn.classList.remove('btn-secondary');
            manualBtn.classList.add('btn-primary', 'active');
            autoBtn.classList.remove('btn-primary', 'active');
            autoBtn.classList.add('btn-secondary');
            manualDefenseBtn.disabled = false;
        }
    }

    // 新增：手动触发防御
    async triggerManualDefense() {
        try {
            const response = await fetch('/api/defense/manual', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    risk_score: parseFloat(document.getElementById('riskScore').textContent) || 0
                })
            });
            
            const result = await response.json();
            if (result.success) {
                this.showNotification('手动防御已触发', 'success');
            } else {
                this.showNotification(result.message, 'error');
            }
            
        } catch (error) {
            console.error('手动触发防御失败:', error);
            this.showNotification('手动触发防御失败', 'error');
        }
    }

    // 新增：关闭防御
    async disableDefense() {
        try {
            const response = await fetch('/api/defense/disable', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.showNotification('防御系统已关闭', 'success');
            } else {
                this.showNotification(result.message, 'error');
            }
            
        } catch (error) {
            console.error('关闭防御失败:', error);
            this.showNotification('关闭防御失败', 'error');
        }
    }
}

// 页面加载完成后初始化仪表板
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
    
    // 修改：每秒更新告警，确保与实时监控同步
    setInterval(() => {
        if (window.dashboard) {
            window.dashboard.updateAlerts();
        }
    }, 1000);  // 从2000改为1000
});

// 预测性分析功能
let predictionChart = null;
let currentPredictionHours = 24;
let aiUpdateInterval = null;
let predictionUpdateInterval = null;

// 添加计时器相关变量
let simulationStartTime = null;
let aiTimer = null;
let predictionTimer = null;
let lastUpdateTime = null;

function initializeAIDashboard() {
    // 初始化预测图表
    initializePredictionChart();
    
    // 设置时间选择器事件监听
    setupTimeSelectors();
    
    // 启动数据更新
    startAIDataUpdates();
    startPredictionUpdates();
    
    // 启动计时器
    startTimers();
    
    console.log('AI Dashboard initialized');
}

function initializePredictionChart() {
    const ctx = document.getElementById('prediction-chart');
    if (!ctx) return;

    predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '攻击概率',
                data: [],
                borderColor: 'rgba(78, 205, 196, 1)',
                backgroundColor: 'rgba(78, 205, 196, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgba(78, 205, 196, 1)',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: 'rgba(78, 205, 196, 0.5)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        title: function(context) {
                            return `时间: ${context[0].label}`;
                        },
                        label: function(context) {
                            return `攻击概率: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        borderColor: 'rgba(255, 255, 255, 0.2)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.8)',
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                        borderColor: 'rgba(255, 255, 255, 0.2)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.8)',
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

function setupTimeSelectors() {
    const selectors = document.querySelectorAll('.time-selector');
    selectors.forEach(selector => {
        selector.addEventListener('click', function() {
            // 移除所有活动状态
            selectors.forEach(s => s.classList.remove('active'));
            // 添加当前活动状态
            this.classList.add('active');
            
            // 更新当前选择的时间
            currentPredictionHours = parseInt(this.dataset.hours);
            
            // 立即更新预测数据
            updatePredictionData();
        });
    });
}

function startAIDataUpdates() {
    updateAIData(); // 立即更新一次
    
    // 每3秒更新一次AI数据
    aiUpdateInterval = setInterval(updateAIData, 3000);
}

function startPredictionUpdates() {
    updatePredictionData(); // 立即更新一次
    
    // 每5秒更新一次预测数据
    predictionUpdateInterval = setInterval(updatePredictionData, 5000);
}

async function updateAIData() {
    try {
        // 获取AI状态
        const aiResponse = await fetch('/api/ai/status');
        const aiData = await aiResponse.json();
        
        // 获取AI历史数据
        const historyResponse = await fetch('/api/ai/history?window_size=10');
        const historyData = await historyResponse.json();
        
        // 更新AI状态指示器
        updateAIStatus(aiData);
        
        // 更新AI指标卡片
        updateAIMetrics(aiData, historyData);
        
    } catch (error) {
        console.error('Failed to update AI data:', error);
        // 显示错误状态
        document.getElementById('ai-status-text').textContent = '连接异常';
    }
}

function updateAIStatus(aiData) {
    const statusText = document.getElementById('ai-status-text');
    const statusDot = document.querySelector('.ai-status-dot');
    
    if (aiData.ai_model_loaded) {
        statusText.textContent = '运行中';
        statusDot.style.background = '#4ecdc4';
    } else {
        statusText.textContent = '仅规则模式';
        statusDot.style.background = '#feca57';
    }
}

function updateAIMetrics(aiData, historyData) {
    // 检测模式
    const modeMap = {
        'hybrid': '混合模式',
        'ai_only': 'AI模式',
        'rule_only': '规则模式'
    };
    document.getElementById('ai-detection-mode').textContent = 
        modeMap[aiData.detection_mode] || '未知模式';
    
    // 风险评分 - 从历史数据获取最新值
    if (historyData.history && historyData.history.length > 0) {
        const latestRecord = historyData.history[historyData.history.length - 1];
        const riskScore = Math.round(latestRecord.risk_score || 0);
        
        document.getElementById('ai-risk-score').textContent = riskScore;
        
        // 更新风险变化指示器
        const changeElement = document.getElementById('ai-risk-change');
        const changeSpan = changeElement.querySelector('span');
        
        if (riskScore > 70) {
            changeElement.className = 'ai-metric-change negative';
            changeSpan.textContent = '高风险';
        } else if (riskScore > 50) {
            changeElement.className = 'ai-metric-change neutral';
            changeSpan.textContent = '中风险';
        } else {
            changeElement.className = 'ai-metric-change positive';
            changeSpan.textContent = '正常';
        }
    }
    
    // 检测准确率 - 基于置信度计算
    const accuracy = Math.round((aiData.ai_weight || 0.7) * 100);
    document.getElementById('ai-accuracy').textContent = accuracy + '%';
    
    // 历史数据点数
    document.getElementById('ai-data-points').textContent = aiData.history_size || 0;
}

async function updatePredictionData() {
    try {
        // 记录更新时间
        lastUpdateTime = Date.now();
        
        // 添加视觉更新指示
        const updateDot = document.getElementById('prediction-update-dot');
        if (updateDot) {
            updateDot.style.animation = 'none';
            updateDot.offsetHeight; // 触发重绘
            updateDot.style.animation = 'updatePulse 2s infinite';
        }
        
        const [probabilityResponse, heatmapResponse, timelineResponse, insightsResponse] = await Promise.all([
            fetch(`/api/prediction/attack-probability?hours=${currentPredictionHours}`),
            fetch(`/api/prediction/heatmap?hours=${currentPredictionHours}`),
            fetch(`/api/prediction/timeline?hours=${currentPredictionHours}`),
            fetch('/api/prediction/insights')
        ]);

        const [probabilityData, heatmapData, timelineData, insightsData] = await Promise.all([
            probabilityResponse.json(),
            heatmapResponse.json(),
            timelineResponse.json(),
            insightsResponse.json()
        ]);

        // 更新图表和显示 - 添加数字变化动画
        updatePredictionChart(probabilityData);
        updateHeatmap(heatmapData);
        updateTimeline(timelineData);
        updateInsights(insightsData);
        
        // 更新最后更新时间显示
        const updateElement = document.getElementById('prediction-last-update');
        if (updateElement) {
            updateElement.textContent = '刚刚更新';
        }
        
        console.log('预测数据更新完成:', {
            dataPoints: probabilityData.data_points_used || 0,
            avgProbability: probabilityData.summary?.average_probability || 0,
            confidence: probabilityData.confidence || 0
        });
        
    } catch (error) {
        console.error('更新预测数据失败:', error);
        showPredictionError();
    }
}

function updatePredictionChart(data) {
    if (!predictionChart || !data.predictions) {
        return;
    }
    
    // 检查是否有错误
    if (data.error) {
        showChartError('prediction-chart', data.error);
        return;
    }
    
    // 准备图表数据
    const labels = data.predictions.map(p => {
        const date = new Date(p.timestamp * 1000);
        return date.getHours() + ':00';
    });
    
    const values = data.predictions.map(p => p.anomaly_probability);
    
    // 更新图表
    predictionChart.data.labels = labels;
    predictionChart.data.datasets[0].data = values;
    predictionChart.update('none');
}

function updateHeatmap(data) {
    const container = document.getElementById('risk-heatmap');
    if (!container) return;
    
    if (data.error) {
        container.innerHTML = `<div class="no-data">
            <div class="no-data-icon">⚠️</div>
            <div class="no-data-text">数据不足</div>
            <div class="no-data-subtext">${data.error}</div>
        </div>`;
        return;
    }
    
    // 创建热力图网格
    const grid = document.createElement('div');
    grid.className = 'heatmap-grid';
    
    // 生成24个小时的热力图格子
    for (let hour = 0; hour < 24; hour++) {
        const cell = document.createElement('div');
        cell.className = 'heatmap-cell';
        
        // 查找对应小时的数据
        const hourData = data.heatmap_data.find(d => d.hour === hour);
        
        if (hourData) {
            const probability = hourData.probability;
            const riskLevel = hourData.risk_level;
            
            cell.classList.add(`risk-${riskLevel}`);
            cell.textContent = hour.toString().padStart(2, '0');
            cell.title = `${hour}:00 - 风险概率: ${probability.toFixed(1)}%`;
        } else {
            cell.classList.add('risk-low');
            cell.textContent = hour.toString().padStart(2, '0');
            cell.title = `${hour}:00 - 无数据`;
        }
        
        grid.appendChild(cell);
    }
    
    container.innerHTML = '';
    container.appendChild(grid);
}

function updateTimeline(data) {
    const container = document.getElementById('risk-timeline');
    if (!container) return;
    
    if (data.error) {
        container.innerHTML = `<div class="no-data">
            <div class="no-data-icon">📅</div>
            <div class="no-data-text">时间线不可用</div>
            <div class="no-data-subtext">${data.error}</div>
        </div>`;
        return;
    }
    
    const timelineHTML = [];
    
    // 添加高风险时段
    if (data.high_risk_periods && data.high_risk_periods.length > 0) {
        data.high_risk_periods.forEach(period => {
            timelineHTML.push(`
                <div class="timeline-item">
                    <div class="timeline-time">${period.hour}:00</div>
                    <div class="timeline-indicator high"></div>
                    <div class="timeline-content">高风险时段</div>
                    <div class="timeline-probability">${period.probability.toFixed(1)}%</div>
                </div>
            `);
        });
    }
    
    // 添加中风险时段
    if (data.medium_risk_periods && data.medium_risk_periods.length > 0) {
        data.medium_risk_periods.slice(0, 3).forEach(period => {
            timelineHTML.push(`
                <div class="timeline-item">
                    <div class="timeline-time">${period.hour}:00</div>
                    <div class="timeline-indicator medium"></div>
                    <div class="timeline-content">中风险时段</div>
                    <div class="timeline-probability">${period.probability.toFixed(1)}%</div>
                </div>
            `);
        });
    }
    
    // 如果没有任何风险时段，显示正常状态
    if (timelineHTML.length === 0) {
        timelineHTML.push(`
            <div class="timeline-item">
                <div class="timeline-time">全天</div>
                <div class="timeline-indicator low"></div>
                <div class="timeline-content">风险水平正常</div>
                <div class="timeline-probability">低</div>
            </div>
        `);
    }
    
    container.innerHTML = timelineHTML.join('');
}

function updateInsights(data) {
    if (!data || !data.insights) return;
    
    const insights = data.insights;
    
    // 添加数字变化动画的辅助函数
    function animateNumber(elementId, newValue, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const currentText = element.textContent;
        const currentValue = parseFloat(currentText) || 0;
        const targetValue = parseFloat(newValue) || 0;
        
        if (currentValue !== targetValue) {
            element.style.transition = 'color 0.3s ease';
            element.style.color = '#ff6b6b'; // 闪烁红色表示变化
            
            setTimeout(() => {
                element.textContent = newValue + suffix;
                element.style.color = '#76b900'; // 恢复绿色
            }, 150);
        } else {
            element.textContent = newValue + suffix;
        }
    }
    
    // 更新短期风险
    if (insights.short_term_risk !== undefined) {
        const riskLevel = insights.short_term_risk > 70 ? '高风险' : 
                         insights.short_term_risk > 40 ? '中等风险' : '低风险';
        animateNumber('short-term-risk', `${insights.short_term_risk.toFixed(1)}% - ${riskLevel}`);
    }
    
    // 更新趋势分析
    if (insights.trend_direction) {
        const trendText = insights.trend_direction === 'increasing' ? '⬆️ 上升' :
                         insights.trend_direction === 'decreasing' ? '⬇️ 下降' : '➡️ 平稳';
        const trendElement = document.getElementById('trend-analysis');
        if (trendElement && trendElement.textContent !== trendText) {
            trendElement.style.transition = 'transform 0.3s ease';
            trendElement.style.transform = 'scale(1.1)';
            setTimeout(() => {
                trendElement.textContent = trendText;
                trendElement.style.transform = 'scale(1)';
            }, 150);
        } else if (trendElement) {
            trendElement.textContent = trendText;
        }
    }
    
    // 更新置信度
    if (insights.confidence !== undefined) {
        const confidencePercent = (insights.confidence * 100).toFixed(1);
        animateNumber('confidence-level', confidencePercent, '%');
    }
    
    // 更新建议操作
    if (insights.recommendation) {
        const recElement = document.getElementById('recommendation');
        if (recElement && recElement.textContent !== insights.recommendation) {
            recElement.style.transition = 'opacity 0.3s ease';
            recElement.style.opacity = '0.5';
            setTimeout(() => {
                recElement.textContent = insights.recommendation;
                recElement.style.opacity = '1';
            }, 150);
        } else if (recElement) {
            recElement.textContent = insights.recommendation;
        }
    }
}

function showChartError(chartId, error) {
    const container = document.getElementById(chartId);
    if (container) {
        const canvas = container.querySelector('canvas');
        if (canvas) {
            canvas.style.display = 'none';
        }
        
        container.innerHTML = `<div class="no-data">
            <div class="no-data-icon">📊</div>
            <div class="no-data-text">图表不可用</div>
            <div class="no-data-subtext">${error}</div>
        </div>`;
    }
}

function showPredictionError() {
    const elements = [
        'prediction-chart',
        'risk-heatmap',
        'risk-timeline',
        'prediction-insights'
    ];
    
    elements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<div class="no-data">
                <div class="no-data-icon">⚠️</div>
                <div class="no-data-text">连接失败</div>
                <div class="no-data-subtext">请检查网络连接</div>
            </div>`;
        }
    });
}

function cleanupAIDashboard() {
    if (aiUpdateInterval) {
        clearInterval(aiUpdateInterval);
    }
    if (predictionUpdateInterval) {
        clearInterval(predictionUpdateInterval);
    }
    if (predictionChart) {
        predictionChart.destroy();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // 等待其他脚本加载完成
    setTimeout(initializeAIDashboard, 100);
});

window.addEventListener('beforeunload', cleanupAIDashboard);

function startTimers() {
    // 设置模拟开始时间
    simulationStartTime = Date.now();
    
    // AI监测计时器 - 每秒更新
    aiTimer = setInterval(() => {
        updateAITimer();
    }, 1000);
    
    // 预测分析计时器 - 每秒更新
    predictionTimer = setInterval(() => {
        updatePredictionTimer();
    }, 1000);
}

function updateAITimer() {
    if (!simulationStartTime) return;
    
    const elapsed = Date.now() - simulationStartTime;
    const hours = Math.floor(elapsed / (1000 * 60 * 60));
    const minutes = Math.floor((elapsed % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((elapsed % (1000 * 60)) / 1000);
    
    const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    const timerElement = document.getElementById('ai-runtime-timer');
    if (timerElement) {
        timerElement.textContent = timeString;
    }
}

function updatePredictionTimer() {
    if (!simulationStartTime) return;
    
    const elapsed = Date.now() - simulationStartTime;
    const hours = Math.floor(elapsed / (1000 * 60 * 60));
    const minutes = Math.floor((elapsed % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((elapsed % (1000 * 60)) / 1000);
    
    const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    const timerElement = document.getElementById('prediction-runtime-timer');
    if (timerElement) {
        timerElement.textContent = timeString;
    }
    
    // 更新最后更新时间
    if (lastUpdateTime) {
        const updateElapsed = Math.floor((Date.now() - lastUpdateTime) / 1000);
        const updateElement = document.getElementById('prediction-last-update');
        if (updateElement) {
            updateElement.textContent = `${updateElapsed}秒前更新`;
        }
    }
}

function stopTimers() {
    if (aiTimer) {
        clearInterval(aiTimer);
        aiTimer = null;
    }
    if (predictionTimer) {
        clearInterval(predictionTimer);
        predictionTimer = null;
    }
    simulationStartTime = null;
} 