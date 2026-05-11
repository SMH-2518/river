FROM python:3.11-slim

# Install Node.js just to build the React frontend
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

WORKDIR /app

# 1. Build React Frontend
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 2. Setup Python Backend
RUN pip install --no-cache-dir -r requirements.txt

# 3. Clean up node_modules to save RAM for the model
RUN rm -rf node_modules

EXPOSE 5000
CMD ["python", "api/app.py"]