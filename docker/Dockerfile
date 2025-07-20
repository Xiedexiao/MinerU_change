FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu22.04

# 创建项目目录
RUN mkdir -p /MinerU
WORKDIR /MinerU


# 拷贝本地项目代码
COPY wan2.1 /wan2.1

# 安装 Python 3.12 及依赖
RUN apt-get update && apt-get install -y \
    python3.12 python3.12-venv python3.12-dev python3-pip \
    build-essential cmake git curl wget libgl1-mesa-glx

# 升级 pip 并使用 Python3.11
RUN python3.12 -m pip install --upgrade pip

# 安装基础 Python 包
RUN pip install packaging modelscope "xfuser>=0.4.1" \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 PyTorch + CUDA 12.8 版本
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 \
    --extra-index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装本地 flash-attn .whl 包
RUN pip install /wan2.1/flash_attn-2.8.0.post2+cu12torch2.5cxx11abiFALSE-cp311-cp311-linux_x86_64.whl

# 安装项目 requirements.txt 中的依赖
RUN pip install -r /wan2.1/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
