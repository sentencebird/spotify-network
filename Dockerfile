FROM python:3.7.12

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /usr/src/app

EXPOSE 8501

CMD ["sh", "-c", "streamlit run --server.port $PORT /usr/src/app.py"]