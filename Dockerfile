# Base image
FROM python:3.11

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install Python packages
RUN pip install --upgrade pip
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt

# Copy app code
COPY . .

# Run Flask
CMD ["python", "app.py"]
