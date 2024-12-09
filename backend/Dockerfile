# Dockerfile for backend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft repository and keys
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql18 \
    mssql-tools18 \
    && rm -rf /var/lib/apt/lists/*

# Add SQL Server tools to PATH
ENV PATH="/opt/mssql-tools18/bin:${PATH}"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application files including available_tags.txt
COPY . .

# Create required directories
RUN mkdir -p /app/configurations \
    /tmp/csv_processor_output && \
    chmod 777 /tmp/csv_processor_output

EXPOSE 5000

CMD ["gunicorn", "--config", "/app/gunicorn.conf.py", "app:app"]