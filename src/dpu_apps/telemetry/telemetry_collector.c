/**
 * @file telemetry_collector.c
 * @brief DPU Telemetry 数据采集模块
 * @author NVIDIA DPU Hackathon Team
 * @date 2024
 */

#include <doca_telemetry.h>
#include <doca_common.h>
#include <doca_log.h>
#include <doca_error.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>

// 网络指标结构体
typedef struct {
    uint64_t timestamp;
    uint64_t packets_per_sec;
    uint64_t bytes_per_sec;
    uint64_t active_connections;
    uint64_t dropped_packets;
    uint64_t encryption_hits;
    uint64_t decryption_hits;
    double cpu_usage;
    double memory_usage;
    uint64_t error_count;
} network_metrics_t;

// 全局变量
static doca_telemetry_t *telemetry_ctx = NULL;
static pthread_t collector_thread;
static int collector_running = 0;
static network_metrics_t current_metrics;

// 回调函数：处理采集到的指标数据
static void
telemetry_callback(const doca_telemetry_data_t *data, void *user_data)
{
    network_metrics_t *metrics = (network_metrics_t *)user_data;
    
    // 获取当前时间戳
    metrics->timestamp = time(NULL);
    
    // 解析网络指标
    metrics->packets_per_sec = doca_telemetry_get_packets_per_sec(data);
    metrics->bytes_per_sec = doca_telemetry_get_bytes_per_sec(data);
    metrics->active_connections = doca_telemetry_get_active_connections(data);
    metrics->dropped_packets = doca_telemetry_get_dropped_packets(data);
    
    // 解析加密指标
    metrics->encryption_hits = doca_telemetry_get_encryption_hits(data);
    metrics->decryption_hits = doca_telemetry_get_decryption_hits(data);
    
    // 解析系统指标
    metrics->cpu_usage = doca_telemetry_get_cpu_usage(data);
    metrics->memory_usage = doca_telemetry_get_memory_usage(data);
    metrics->error_count = doca_telemetry_get_error_count(data);
    
    // 打印调试信息
    DOCA_LOG_INFO("Telemetry collected: PPS=%lu, BPS=%lu, Conn=%lu, Drops=%lu",
                  metrics->packets_per_sec, metrics->bytes_per_sec,
                  metrics->active_connections, metrics->dropped_packets);
}

// 数据采集线程
static void *
collector_thread_func(void *arg)
{
    doca_error_t result;
    
    while (collector_running) {
        // 触发数据采集
        result = doca_telemetry_collect(telemetry_ctx, telemetry_callback, &current_metrics);
        if (result != DOCA_SUCCESS) {
            DOCA_LOG_ERR("Failed to collect telemetry data: %s", doca_error_get_descr(result));
        }
        
        // 等待下一次采集 (100ms 间隔)
        usleep(100000);
    }
    
    return NULL;
}

/**
 * @brief 初始化 Telemetry 采集器
 * @param device_id DPU 设备 ID
 * @return DOCA_SUCCESS 成功，其他值失败
 */
doca_error_t
telemetry_collector_init(const char *device_id)
{
    doca_error_t result;
    doca_telemetry_config_t config;
    
    // 初始化 DOCA 日志
    result = doca_log_create("telemetry_collector");
    if (result != DOCA_SUCCESS) {
        return result;
    }
    
    // 配置 Telemetry
    result = doca_telemetry_config_create(&config);
    if (result != DOCA_SUCCESS) {
        DOCA_LOG_ERR("Failed to create telemetry config: %s", doca_error_get_descr(result));
        return result;
    }
    
    // 设置设备 ID
    result = doca_telemetry_config_set_device_id(config, device_id);
    if (result != DOCA_SUCCESS) {
        DOCA_LOG_ERR("Failed to set device ID: %s", doca_error_get_descr(result));
        doca_telemetry_config_destroy(config);
        return result;
    }
    
    // 设置采集间隔 (100ms)
    result = doca_telemetry_config_set_interval(config, 100);
    if (result != DOCA_SUCCESS) {
        DOCA_LOG_ERR("Failed to set collection interval: %s", doca_error_get_descr(result));
        doca_telemetry_config_destroy(config);
        return result;
    }
    
    // 创建 Telemetry 上下文
    result = doca_telemetry_create(config, &telemetry_ctx);
    if (result != DOCA_SUCCESS) {
        DOCA_LOG_ERR("Failed to create telemetry context: %s", doca_error_get_descr(result));
        doca_telemetry_config_destroy(config);
        return result;
    }
    
    // 启动采集线程
    collector_running = 1;
    if (pthread_create(&collector_thread, NULL, collector_thread_func, NULL) != 0) {
        DOCA_LOG_ERR("Failed to create collector thread");
        doca_telemetry_destroy(telemetry_ctx);
        doca_telemetry_config_destroy(config);
        return DOCA_ERROR_UNKNOWN;
    }
    
    doca_telemetry_config_destroy(config);
    DOCA_LOG_INFO("Telemetry collector initialized successfully");
    
    return DOCA_SUCCESS;
}

/**
 * @brief 获取当前网络指标
 * @param metrics 输出指标数据
 * @return DOCA_SUCCESS 成功，其他值失败
 */
doca_error_t
telemetry_get_current_metrics(network_metrics_t *metrics)
{
    if (metrics == NULL) {
        return DOCA_ERROR_INVALID_VALUE;
    }
    
    // 复制当前指标数据
    memcpy(metrics, &current_metrics, sizeof(network_metrics_t));
    
    return DOCA_SUCCESS;
}

/**
 * @brief 停止 Telemetry 采集器
 */
void
telemetry_collector_cleanup(void)
{
    if (collector_running) {
        collector_running = 0;
        pthread_join(collector_thread, NULL);
    }
    
    if (telemetry_ctx != NULL) {
        doca_telemetry_destroy(telemetry_ctx);
        telemetry_ctx = NULL;
    }
    
    DOCA_LOG_INFO("Telemetry collector cleaned up");
}

/**
 * @brief 计算风险评分 (基于当前指标)
 * @param metrics 网络指标
 * @return 风险评分 (0-100)
 */
int
calculate_risk_score(const network_metrics_t *metrics)
{
    int risk_score = 0;
    
    // 基于丢包率计算风险
    if (metrics->dropped_packets > 1000) {
        risk_score += 20;
    } else if (metrics->dropped_packets > 100) {
        risk_score += 10;
    }
    
    // 基于连接数异常计算风险
    if (metrics->active_connections > 10000) {
        risk_score += 25;
    } else if (metrics->active_connections > 5000) {
        risk_score += 15;
    }
    
    // 基于错误计数计算风险
    if (metrics->error_count > 100) {
        risk_score += 30;
    } else if (metrics->error_count > 50) {
        risk_score += 20;
    }
    
    // 基于 CPU 使用率计算风险
    if (metrics->cpu_usage > 80.0) {
        risk_score += 15;
    } else if (metrics->cpu_usage > 60.0) {
        risk_score += 10;
    }
    
    // 限制最大风险分数
    if (risk_score > 100) {
        risk_score = 100;
    }
    
    return risk_score;
} 