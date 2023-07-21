FROM python:3.11
WORKDIR /app
COPY dev-requirements.txt dev-requirements.txt
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]