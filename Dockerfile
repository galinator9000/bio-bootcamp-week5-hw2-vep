FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /data
COPY data/* /data/

COPY . .

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Entrypoint for running the script
CMD ["python", "src/import_vep_data.py"]