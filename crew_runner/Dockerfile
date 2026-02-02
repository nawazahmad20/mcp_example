FROM python:3.12-slim

WORKDIR /app

# Optional but handy: curl for debugging inside the container
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the runner and helper modules
COPY *.py .

CMD ["python", "-u", "run_crewai_with_mcp.py"]
