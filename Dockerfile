FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (already in base image, but ensure deps)
RUN playwright install chromium
RUN playwright install-deps

# Copy application code
COPY . .

# Expose port
EXPOSE 10000

# Set environment variables
ENV PORT=10000
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=wsgi.py

# Run the application with Gunicorn
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:10000", "--workers", "2", "--timeout", "120"]

