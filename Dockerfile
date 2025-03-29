# Use official Python image
FROM python:3.12

# Set working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code into the container
COPY . .

# Expose port 5000 for Flask
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "backend.py"]
