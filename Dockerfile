# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Flask app code to the working directory
COPY .. .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the Flask app will run on
EXPOSE 5000

# Set the entrypoint command
CMD ["python", "app.py"]