# Use official Python base image changed
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
COPY chat_hf.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "chat_hf.py"]
