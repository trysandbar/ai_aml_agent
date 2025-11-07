FROM python:3.13-slim

# Install Node.js and npm for Puppeteer MCP server
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variable for unbuffered Python output
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "-u", "tests/test_agent_amazon.py"]
