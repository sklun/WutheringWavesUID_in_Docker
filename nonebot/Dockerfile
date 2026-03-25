FROM python:3.12 AS requirements_stage

WORKDIR /wheel

RUN python -m pip install --user uv

COPY ./app/pyproject.toml /wheel/

RUN python -m uv tool run --no-cache --from nb-cli nb generate -f /tmp/bot.py

FROM python:3.12-slim

WORKDIR /app

ENV TZ=Asia/Shanghai
ENV PYTHONPATH=/app

COPY --from=requirements_stage /tmp/bot.py /app
COPY ./app /app/

RUN pip install --no-cache-dir nonebot2 \
  && pip install --no-cache-dir .

CMD ["python", "bot.py"]
