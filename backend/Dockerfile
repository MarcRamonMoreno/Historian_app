FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl gnupg2 \
    unixodbc unixodbc-dev tdsodbc freetds-bin freetds-dev

RUN apt-get install -y iputils-ping && \
ping -c 2 172.16.0.1

# Add Microsoft repo and install SQL Server ODBC driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Configure ODBC and FreeTDS
COPY odbc.ini /etc/odbc.ini
COPY freetds.conf /etc/freetds/freetds.conf

# Set environment variables for timeouts
ENV ODBCSQL_LOGIN_TIMEOUT=30
ENV ODBCSQL_QUERY_TIMEOUT=30

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pyodbc gunicorn

COPY . .
RUN mkdir -p /app/configurations /tmp/csv_processor_output && chmod 777 /tmp/csv_processor_output

EXPOSE 5000
CMD ["gunicorn", "--config", "/app/gunicorn.conf.py", "app:app"]