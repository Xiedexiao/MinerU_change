FROM mineru-sglang:20250720

RUN mkdir -p /sgl-workspace/sglang/api_fast

COPY api_fast /sgl-workspace/sglang/api_fast

RUN python3 -m pip install -r /sgl-workspace/sglang/api_fast/requirements.txt -i https://mirrors.aliyun.com/pypi/simple



ENTRYPOINT [ "/bin/bash", "/sgl-workspace/sglang/api_fast/entrypoint.sh"]

