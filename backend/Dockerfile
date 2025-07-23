# Use official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# Set the port for Cloud Run
ENV PORT 8080

# Run Gunicorn server
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
