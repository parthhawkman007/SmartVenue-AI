# Use the official lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the backend requirements over and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code to the container
COPY backend ./backend

# Expose port (Cloud Run defaults to 8080)
EXPOSE 8080

# Configure environment variables
ENV PORT=8080
ENV PYTHONPATH=/app

# Start the FastAPI application
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8080"]
