FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY main.py .
COPY app.py .
COPY register_model.py .
COPY templates/ templates/

EXPOSE 5001

CMD ["python", "app.py"]