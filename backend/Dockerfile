# Use a lightweight Python base image
FROM python:3.11-slim

# Install PostgreSQL client (for pg_isready)
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose FastAPI port
EXPOSE 8000

# Run startup script (wait for DB, migrate, then start app)
CMD ["./start.sh"]
