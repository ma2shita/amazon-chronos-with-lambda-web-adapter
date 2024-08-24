# syntax=docker/dockerfile:1
FROM public.ecr.aws/docker/library/python:3.12-slim AS downloader
RUN python3 -m pip install "huggingface_hub[cli]"
ENV HF_HOME=/tmp/hf_home/
RUN huggingface-cli download amazon/chronos-t5-tiny

FROM public.ecr.aws/docker/library/python:3.12-slim AS base
# Including AWS Lambda Web Adapter layer
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 /lambda-adapter /opt/extensions/lambda-adapter
# Deploy Timeseries FM
## `HF_HOME=/tmp/home/` for avoid `There was a problem when trying to write in your cache folder ...` message. TRANSFORMERS_CACHE will be obsolete. (the dir required write permission)
ENV HF_HOME=/tmp/hf_home/
COPY --from=downloader /tmp/hf_home/ /tmp/hf_home/
# Setup App
WORKDIR /var/task/
RUN apt-get update && apt-get install -y git && apt-get autoremove --purge -y && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --no-cache-dir -U pip && python3 -m pip install --no-cache-dir git+https://github.com/amazon-science/chronos-forecasting.git
RUN python3 -m pip install --no-cache-dir uvicorn fastapi pandas matplotlib
## for avoid `Matplotlib created a temporary cache directory ...` message. (the dir required write permission)
ENV MPLCONFIGDIR=/tmp/matplotlib/
COPY *.py ./

FROM base AS prod_runner
SHELL ["/bin/bash", "-c"]
CMD uvicorn --port=8080 main:app

FROM base AS test_runner
RUN python3 -m pip install --no-cache-dir pytest httpx
RUN python3 -m pytest -s test_main.py
