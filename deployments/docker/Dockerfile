# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

# Install dependencies and the package itself using uv
# uv sync installs all dependencies and the workspace packages
RUN uv sync --frozen --no-dev

# Expose port 8000
EXPOSE 8000

# Command to run the application
# uv run automatically uses the venv created by uv sync
CMD ["uv", "run", "uvicorn", "casa_auth_server.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
