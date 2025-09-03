#!/bin/bash

# NVIDIA DPU 网络安全防御系统启动脚本
# 作者: 崔湛林 (新南威尔士大学)

echo "🚀 启动 NVIDIA DPU 网络安全防御系统"
echo "=================================="

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python版本检查通过: $python_version"
else
    echo "❌ Python版本过低，需要3.8+，当前版本: $python_version"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖包..."
if ! python3 -c "import flask, numpy" 2>/dev/null; then
    echo "⚠️  缺少必要依赖，正在安装..."
    pip install -r requirements.txt
fi

# 检查AI依赖（可选）
if [ -f "requirements_ai.txt" ]; then
    if ! python3 -c "import torch" 2>/dev/null; then
        echo "⚠️  缺少AI依赖，正在安装..."
        pip install -r requirements_ai.txt
    fi
fi

echo "✅ 依赖检查完成"

# 启动系统
echo "🌐 启动Web服务..."
echo "📍 访问地址: http://localhost:5002"
echo "🛑 按 Ctrl+C 停止服务"
echo ""

python3 app.py
