# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your app runs on (e.g., 8000)
EXPOSE 8000

# Command to run your Python app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]