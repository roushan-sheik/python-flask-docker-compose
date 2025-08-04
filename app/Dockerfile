# Use a valid Python image
FROM python:3.10-slim

# Install netcat for database connection checking
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create scripts directory
RUN mkdir -p scripts

# Copy the rest of the application code
COPY . .

# Make sure the runner script is executable
RUN chmod +x scripts/runner.sh

# Expose the port Flask will run on
EXPOSE 5000

# Run the Flask app using the runner script
CMD ["sh", "scripts/runner.sh"]