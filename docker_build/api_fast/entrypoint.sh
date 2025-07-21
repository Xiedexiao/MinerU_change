#! /bin/bash

export MINERU_MODEL_SOURCE=local


# 读取环境变量
env=${START_TYPE}

if [ "$env" = "sglang" ]; then
    echo "当前环境：开发环境, 启动sglang-server"
    nohup uvicorn api_fast.server_fast:app --host 0.0.0.0 --port 8000 > logs/fastapi.log 2>&1 &
    mineru-sglang-server --host 0.0.0.0 --port 30000
elif [ "$env" = "api" ]; then
    echo "当前环境：测试环境，启动api服务"
    mineru-api --host 0.0.0.0 --port 8000
elif [ "$env" = "gradio" ]; then
    echo "当前环境：生产环境，启动gradio服务"
    mineru-gradio --host 0.0.0.0 --port 8000 --enable-sglang-engine true
else
    echo "未知环境变量: $env"
    # 可选：执行默认命令或退出
    exit 1
fi