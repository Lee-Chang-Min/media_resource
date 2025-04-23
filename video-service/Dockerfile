FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh /usr/wait-for-it.sh

RUN chmod +x /usr/wait-for-it.sh 

COPY . .

#DB 연결 후 서버 실행
CMD ["/usr/wait-for-it.sh", "postgres:5432", "--timeout=0", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"] 