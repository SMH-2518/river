# Start with Python (easier for TensorFlow)
FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node requirements
COPY package*.json ./
RUN npm install

# Copy the rest of the code
COPY . .

# Render uses the PORT env variable
EXPOSE 3000

CMD ["npm", "start"]