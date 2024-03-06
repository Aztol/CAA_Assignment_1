# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the app dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source code to the working directory
COPY main.py .

# Set the command to run your app when the container starts
CMD ["python", "main.py"]