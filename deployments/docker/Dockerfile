# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv for fast Python package management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Copy source code
COPY src/ ./src/

# Copy license and README files
COPY LICENSE README.md ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["uv", "run", "uvicorn", "identity_auth_server.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
