# Use an official Python runtime as a parent image
FROM python:3.13.4-slim

# Set the working directory in the container
WORKDIR /app


RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*


# Copy the current directory contents into the container
COPY . /app



# Install dependencies
RUN pip install -r requirements.txt

# Ensure wait-for-it.sh is executable
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Expose port 5000
EXPOSE 5000

# Define environment variables (for production)
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Run the Flask app with wait-for-it to ensure MySQL is ready
CMD ["./wait-for-it.sh", "ecommerce-db:3306", "--", "python3", "app.py"]
