# Use Python 3.10 slim image for a minimal footprint
FROM python:3.10-slim

# Set the working directory directly in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run FastAPI app using uvicorn on port 8080 and host 0.0.0.0
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
