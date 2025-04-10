# Use GDAL as the base image
FROM ghcr.io/osgeo/gdal:ubuntu-small-latest

# Install Python, pip, and python venv
RUN apt-get update && apt-get install -y \
    python3 python3-venv python3-pip

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/requirements.txt

RUN python3 -m venv /venv

ENV PATH="/venv/bin:$PATH"

RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Copy the application files
COPY src/ ./src/

# Copy the .env file
COPY .env .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]