FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY utils.py .

# Copy all collections (assuming they’re in root)
COPY Collection* ./Collection*/

CMD ["python", "main.py"]
