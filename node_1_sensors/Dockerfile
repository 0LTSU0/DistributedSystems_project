FROM python:3.9.7

WORKDIR /node_1
COPY . /node_1

RUN pip install -r requirements.txt


CMD ["python", "coordinator.py", "--rcv_threads", "2", "--mode", "kafka", "--timeout", "30"]
