// 国际化语言配置
const i18n = {
    zh: {
        // 页面标题
        title: "AI 驱动的 DPU 实时网络风险预警与自动防御系统",
        subtitle: "NVIDIA DPU Hackthon Team Horizon Publish",
        
        // 控制面板
        controlPanel: "控制面板",
        startSimulation: "启动模拟",
        stopSimulation: "停止模拟",
        triggerDDoS: "触发DDoS",
        triggerResource: "触发资源耗尽",
        auto: "自动",
        manual: "手动",
        manualDefense: "手动防御",
        disableDefense: "关闭防御",
        
        // 指标标签
        riskScore: "风险评分",
        systemStatus: "系统状态",
        packetsPerSec: "数据包/秒",
        activeConnections: "活跃连接",
        
        // 状态文本
        normal: "正常",
        warning: "警告",
        danger: "危险",
        noAlerts: "暂无告警",
        
        // 卡片标题
        realTimeMonitoring: "实时监控",
        realTimeAlerts: "实时告警",
        networkMetrics: "网络指标详情",
        defenseStatus: "防御状态",
        
        // 网络指标详情
        bytesPerSec: "字节/秒",
        droppedPackets: "丢包数",
        encryptionHits: "加密命中",
        cpuUsage: "CPU使用率",
        memoryUsage: "内存使用率",
        errorCount: "错误计数",
        
        // 防御状态
        defenseActive: "防御状态",
        defenseMode: "防御模式",
        activeRules: "活跃规则",
        lastTrigger: "最后触发",
        defenseEffectiveness: "防御效果",
        notActive: "未激活",
        
        // 通知消息
        simulationStarted: "模拟已启动",
        simulationStopped: "模拟已停止",
        ddosTriggered: "DDoS攻击已触发",
        resourceTriggered: "资源耗尽已触发",
        defenseActivated: "防御已激活",
        defenseDisabled: "防御已关闭",
        modeChanged: "模式已切换",
        
        // 图表标签
        time: "时间",
        riskScoreChart: "风险评分",
        packetsPerSecChart: "数据包/秒"
    },
    
    en: {
        // Page title
        title: "AI-Powered DPU Real-time Network Risk Warning and Auto-Defense System",
        subtitle: "NVIDIA DPU Hackathon Team Horizon Publish",
        
        // Control panel
        controlPanel: "Control Panel",
        startSimulation: "Start Simulation",
        stopSimulation: "Stop Simulation",
        triggerDDoS: "Trigger DDoS",
        triggerResource: "Trigger Resource Exhaustion",
        auto: "Auto",
        manual: "Manual",
        manualDefense: "Manual Defense",
        disableDefense: "Disable Defense",
        
        // Metric labels
        riskScore: "Risk Score",
        systemStatus: "System Status",
        packetsPerSec: "Packets/sec",
        activeConnections: "Active Connections",
        
        // Status text
        normal: "Normal",
        warning: "Warning",
        danger: "Danger",
        noAlerts: "No Alerts",
        
        // Card titles
        realTimeMonitoring: "Real-time Monitoring",
        realTimeAlerts: "Real-time Alerts",
        networkMetrics: "Network Metrics Details",
        defenseStatus: "Defense Status",
        
        // Network metrics details
        bytesPerSec: "Bytes/sec",
        droppedPackets: "Dropped Packets",
        encryptionHits: "Encryption Hits",
        cpuUsage: "CPU Usage",
        memoryUsage: "Memory Usage",
        errorCount: "Error Count",
        
        // Defense status
        defenseActive: "Defense Status",
        defenseMode: "Defense Mode",
        activeRules: "Active Rules",
        lastTrigger: "Last Trigger",
        defenseEffectiveness: "Defense Effectiveness",
        notActive: "Not Active",
        
        // Notification messages
        simulationStarted: "Simulation started",
        simulationStopped: "Simulation stopped",
        ddosTriggered: "DDoS attack triggered",
        resourceTriggered: "Resource exhaustion triggered",
        defenseActivated: "Defense activated",
        defenseDisabled: "Defense disabled",
        modeChanged: "Mode changed",
        
        // Chart labels
        time: "Time",
        riskScoreChart: "Risk Score",
        packetsPerSecChart: "Packets/sec"
    }
};

// 当前语言
let currentLanguage = 'zh';

// 语言切换函数
function switchLanguage(lang) {
    if (i18n[lang]) {
        currentLanguage = lang;
        updatePageLanguage();
        localStorage.setItem('language', lang);
    }
}

// 获取翻译文本
function t(key) {
    return i18n[currentLanguage][key] || i18n['zh'][key] || key;
}

// 更新页面语言
function updatePageLanguage() {
    // 更新页面标题
    document.title = t('title');
    
    // 更新HTML lang属性
    document.documentElement.lang = currentLanguage === 'zh' ? 'zh-CN' : 'en';
    
    // 更新主标题
    const titleElement = document.querySelector('.header-title');
    if (titleElement) {
        titleElement.innerHTML = `<i class="fas fa-shield-alt"></i> ${t('title')}`;
    }
    
    // 更新副标题
    const subtitleElement = document.querySelector('.header-subtitle');
    if (subtitleElement) {
        subtitleElement.textContent = t('subtitle');
    }
    
    // 更新控制面板
    updateControlPanel();
    
    // 更新指标标签
    updateMetrics();
    
    // 更新卡片标题
    updateCardTitles();
    
    // 更新详细信息
    updateDetails();
    
    // 更新图表
    updateCharts();
}

// 更新控制面板
function updateControlPanel() {
    const elements = {
        'controlPanel': '.card-header h5',
        'startSimulation': '#startSimulation',
        'stopSimulation': '#stopSimulation',
        'triggerDDoS': '#triggerDDoS',
        'triggerResource': '#triggerResource',
        'auto': '#autoMode',
        'manual': '#manualMode',
        'manualDefense': '#manualDefense',
        'disableDefense': '#disableDefense'
    };
    
    for (const [key, selector] of Object.entries(elements)) {
        const element = document.querySelector(selector);
        if (element) {
            if (key === 'controlPanel') {
                element.innerHTML = `<i class="fas fa-cogs"></i> ${t(key)}`;
            } else {
                const icon = element.querySelector('i');
                const iconClass = icon ? icon.className : '';
                element.innerHTML = icon ? `<i class="${iconClass}"></i> ${t(key)}` : t(key);
            }
        }
    }
}

// 更新指标标签
function updateMetrics() {
    const elements = {
        'riskScore': '.metric-card:nth-child(1) .metric-label',
        'systemStatus': '.metric-card:nth-child(2) .metric-label',
        'packetsPerSec': '.metric-card:nth-child(3) .metric-label',
        'activeConnections': '.metric-card:nth-child(4) .metric-label'
    };
    
    for (const [key, selector] of Object.entries(elements)) {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = t(key);
        }
    }
}

// 更新卡片标题
function updateCardTitles() {
    const elements = {
        'realTimeMonitoring': '.charts-row .card:nth-child(1) .card-header h5',
        'realTimeAlerts': '.charts-row .card:nth-child(2) .card-header h5',
        'networkMetrics': '.details-row .card:nth-child(1) .card-header h5',
        'defenseStatus': '.details-row .card:nth-child(2) .card-header h5'
    };
    
    for (const [key, selector] of Object.entries(elements)) {
        const element = document.querySelector(selector);
        if (element) {
            const icon = element.querySelector('i');
            const iconClass = icon ? icon.className : '';
            element.innerHTML = icon ? `<i class="${iconClass}"></i> ${t(key)}` : t(key);
        }
    }
}

// 更新详细信息
function updateDetails() {
    // 更新网络指标详情
    const networkLabels = {
        'bytesPerSec': '字节/秒:',
        'droppedPackets': '丢包数:',
        'encryptionHits': '加密命中:',
        'cpuUsage': 'CPU使用率:',
        'memoryUsage': '内存使用率:',
        'errorCount': '错误计数:'
    };
    
    for (const [key, selector] of Object.entries(networkLabels)) {
        const element = document.querySelector(`[id="${key}"]`).parentElement;
        if (element) {
            element.innerHTML = `<strong>${t(key)}:</strong> <span id="${key}">0</span>`;
        }
    }
    
    // 更新防御状态
    const defenseLabels = {
        'defenseActive': '防御状态:',
        'defenseMode': '防御模式:',
        'activeRules': '活跃规则:',
        'lastTrigger': '最后触发:',
        'defenseEffectiveness': '防御效果:'
    };
    
    for (const [key, selector] of Object.entries(defenseLabels)) {
        const element = document.querySelector(`[id="${key}"]`).parentElement;
        if (element) {
            element.innerHTML = `<strong>${t(key)}:</strong> <span id="${key}">${key === 'defenseActive' ? t('notActive') : '-'}</span>`;
        }
    }
}

// 更新图表
function updateCharts() {
    if (window.dashboard && window.dashboard.chart) {
        const chart = window.dashboard.chart;
        
        // 更新图表标签
        chart.options.scales.x.title.text = t('time');
        chart.options.scales.y.title.text = t('riskScoreChart');
        chart.options.scales.y1.title.text = t('packetsPerSecChart');
        
        // 更新数据集标签
        chart.data.datasets[0].label = t('riskScoreChart');
        chart.data.datasets[1].label = t('packetsPerSecChart');
        
        chart.update();
    }
}

// 初始化语言
function initLanguage() {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage && i18n[savedLanguage]) {
        currentLanguage = savedLanguage;
    }
    updatePageLanguage();
}

// 导出函数
window.i18n = {
    t,
    switchLanguage,
    initLanguage,
    currentLanguage: () => currentLanguage
}; 