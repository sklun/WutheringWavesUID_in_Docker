# ==========================================
# Stage 0: 参数
# ==========================================
# 原始镜像 astral/uv:python3.12-bookworm-slim
# cnb.cool 镜像 docker.cnb.cool/gscore-mirror/docker-sync/astral-uv:python3.12-bookworm-slim

# 定义基础镜像的参数
ARG GSCORE_BASE_IMAGE=docker.cnb.cool/gscore-mirror/docker-sync/astral-uv:python3.12-bookworm-slim
#ARG GSCORE_BASE_IMAGE=docker.cnb.cool/gscore-mirror/gscore-docker:latest
ARG GSCORE_PYTHON_INDEX=https://pypi.org/simple

# ==========================================
# Stage 1: Base (基础系统环境)
# ==========================================
FROM ${GSCORE_BASE_IMAGE} AS base

USER root

EXPOSE 8765

WORKDIR /gsuid_core

ENV UV_PROJECT_ENVIRONMENT=/venv
ENV PATH="/venv/bin:$PATH"
ENV UV_LINK_MODE=copy



RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    gcc \
    python3-dev \
    build-essential \
    tzdata \
    && ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo Asia/Shanghai > /etc/timezone \
    && uv venv /venv --seed \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 添加 Nodejs
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs npm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN git config --global --add safe.directory '*'

# ==========================================
# Stage 2: Playwright Base (浏览器环境层)
# ==========================================
FROM base AS playwright_base

ARG GSCORE_PYTHON_INDEX

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN --mount=type=cache,target=/root/.cache/uv \
    apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-cjk \
    libffi-dev \
    && uv pip install playwright --index ${GSCORE_PYTHON_INDEX} \
    && playwright install --with-deps chromium \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ==========================================
# Stage 3: Runtime (挂载模式)
# ==========================================
FROM playwright_base AS runtime

CMD ["uv", "run", "--python", "/venv/bin/python", "core", "--host", "0.0.0.0"]
