FROM python:3.11-slim

# Install Node.js, pnpm, gettext, and nginx
RUN apt-get update && apt-get install -y curl gettext git nginx
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g pnpm

# Install uv (fast Python package manager that supports dependency-groups)
RUN pip install uv

# Set up working directory
WORKDIR /app
COPY . /app

# Install Python dependencies for Kolibri
ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.16.0
RUN mkdir -p kolibri/dist && touch kolibri/dist/__init__.py
RUN uv pip install --system -e . --group base --group dev

# Install frontend dependencies
RUN pnpm install --shamefully-hoist

# Patch babel.config.js to use absolute path so Docker can resolve it
RUN echo "module.exports = require('/app/packages/kolibri-jest-config/jest.conf/babel.config');" > babel.config.js

# Build the Kolibri frontend
RUN pnpm run build

# --- Nginx config ---
# Routes /zipcontent/ to internal zip content server (port 8081)
# Routes everything else to Kolibri main server (port 8000)
RUN cat > /etc/nginx/sites-available/default <<'NGINXEOF'
server {
    listen 8080;

    # Proxy Flexbook/HTML5 zip content server
    location /zipcontent/ {
        proxy_pass http://127.0.0.1:8081/zipcontent/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120;
    }

    # Proxy main Kolibri Django server
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }
}
NGINXEOF

# --- Startup script ---
# Writes options.ini to guarantee ZIP_CONTENT_ORIGIN is applied,
# then starts nginx and kolibri together
RUN cat > /start.sh <<'STARTEOF'
#!/bin/bash
set -e

# Create Kolibri home and write options.ini to force same-origin zip content
mkdir -p /root/.kolibri
cat > /root/.kolibri/options.ini <<OPTEOF
[Deployment]
ZIP_CONTENT_ORIGIN = https://lms-online-qvbg.onrender.com
OPTEOF

echo "==> Starting nginx..."
nginx

echo "==> Starting Kolibri on port 8000 (zip content on port 8081)..."
exec kolibri start --port=8000 --zip-port=8081 --foreground
STARTEOF

RUN chmod +x /start.sh

# Configure Kolibri for production server mode
ENV KOLIBRI_RUN_MODE=prod
ENV KOLIBRI_LISTEN_ADDRESS=0.0.0.0

# Render exposes only one port (8080) — nginx listens here and proxies internally
EXPOSE 8080

CMD ["/start.sh"]
