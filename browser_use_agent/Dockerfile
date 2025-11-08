# Browser-Use Agent Dockerfile
# Simpler than MCP version - no Node.js or MCP servers needed!

FROM python:3.13-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium --with-deps

# Copy application code
COPY . .

# Create audit logs directory
RUN mkdir -p /app/audit_logs

# Set entrypoint
ENTRYPOINT ["python", "run_workflow.py"]
