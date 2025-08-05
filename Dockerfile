FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# RUN apt-get update && apt-get install -y --no-install-recommends wget

RUN mkdir -p /data

COPY data/* /data/

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Entrypoint for running the script
CMD ["python", "src/import_vep_data.py"]