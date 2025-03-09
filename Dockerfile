FROM python:3.11-slim-bullseye AS builder
RUN apt-get update; apt-get -y upgrade; apt-get clean; apt-get install binutils git -y

RUN pip3 install --no-cache-dir PyInstaller loguru prometheus_client click pyyaml
RUN pip3 install git+https://github.com/almottier/TapoP100.git@main


COPY . /app
WORKDIR /app

RUN python3 -m PyInstaller main.py --onefile --hidden-import loguru --hidden-import prometheus_client --hidden-import PyP100

FROM python:3.11-slim-bullseye
COPY --from=builder /app/dist /app/dist

CMD /app/dist/main --tapo-email=$TAPO_EMAIL --tapo-password=$TAPO_PASSWORD --config-file=/app/tapo.yaml --prometheus-port=$PORT
