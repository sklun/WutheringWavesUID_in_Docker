FROM python:alpine

WORKDIR /app
COPY ./app /app

RUN pip install nb-cli \
    nonebot2[fastapi] \
    nonebot-adapter-onebot
RUN nb plugin install nonebot-plugin-genshinuid

ENV TZ=Asia/Shanghai
CMD ["nb", "run"]
