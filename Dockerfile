# 1. Use a lightweight Python base image (Slim version is faster)
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy only the requirements first (Docker caches this layer!)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code
COPY . .

# 6. Expose the port Flask runs on
EXPOSE 5000

# 7. The command to start the app
CMD ["python", "app.py"]