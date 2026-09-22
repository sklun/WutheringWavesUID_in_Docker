# The upstream mount-mode image provides Python, uv, browser system
# dependencies, and CJK fonts. Project dependencies and the matching browser
# are synchronized into the persistent runtime volume from uv.lock.
ARG GSCORE_BASE_IMAGE=docker.cnb.cool/gscore-mirror/gsuid_core/gscore-uv-3.12:latest

FROM ${GSCORE_BASE_IMAGE} AS runtime

ENV UV_PROJECT_ENVIRONMENT=/runtime/venv \
    UV_CACHE_DIR=/runtime/uv-cache \
    UV_LINK_MODE=copy \
    PLAYWRIGHT_BROWSERS_PATH=/runtime/ms-playwright \
    PATH="/runtime/venv/bin:${PATH}"

EXPOSE 8765
WORKDIR /gsuid_core

COPY --chmod=755 gscore-entrypoint.sh /usr/local/bin/gscore-entrypoint

ENTRYPOINT ["gscore-entrypoint"]
CMD ["core", "--host", "0.0.0.0"]
