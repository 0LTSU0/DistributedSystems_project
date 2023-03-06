FROM python:latest

WORKDIR /node_3
COPY . /node_3

RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "data_visualizer.py"]
