FROM python
ENV TZ=Asia/Shanghai
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY ./app /app
RUN pip install --no-cache-dir .

CMD ["nb", "run"]
