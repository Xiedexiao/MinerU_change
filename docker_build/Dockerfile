FROM mineru-sglang:20250720

RUN mkdir -p /sgl-workspace/sglang/api_fast
RUN mkdir -p /sgl-workspace/sglang/logs

COPY api_fast/ /sgl-workspace/sglang/api_fast
# COPY api_fast/server_fast.py /sgl-workspace/sglang/

RUN python3 -m pip install -r /sgl-workspace/sglang/api_fast/requirements.txt -i https://mirrors.aliyun.com/pypi/simple && \
    python3 -m pip cache purge
RUN chmod +x /sgl-workspace/sglang/api_fast/entrypoint.sh


ENTRYPOINT [ "/bin/bash", "/sgl-workspace/sglang/api_fast/entrypoint.sh"]

