FROM python:latest

WORKDIR /node_2
COPY . /node_2

RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "flask_server.py"]
