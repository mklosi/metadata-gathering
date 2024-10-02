# Use the official Python image from the Docker hub
FROM python:3.10-slim

# Copy the current directory contents into the container at /app
COPY server/ /app

# Set the working directory in the container to /app
WORKDIR /app

# Install previously-generated dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Flask app will run on
EXPOSE 4000

# Define the command to run the application
CMD ["python", "app.py"]
