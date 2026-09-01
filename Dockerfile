FROM python:3.11-slim

# Install Node.js, pnpm, gettext, nginx, and supervisor
RUN apt-get update && apt-get install -y curl gettext git nginx supervisor
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
# Routes:
#   /zipcontent/ → Kolibri zip content server on port 8081
#   /           → Kolibri main server on port 8000
RUN cat > /etc/nginx/sites-available/default <<'EOF'
server {
    listen 8080;

    # Proxy zip content server (Flexbooks, HTML5 apps)
    location /zipcontent/ {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy main Kolibri server
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
EOF

# --- Supervisor config to run nginx + kolibri together ---
RUN cat > /etc/supervisor/conf.d/kolibri.conf <<'EOF'
[supervisord]
nodaemon=true
logfile=/dev/null
logfile_maxbytes=0

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:kolibri]
command=kolibri start --port=8000 --zip-port=8081 --foreground
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF

# Configure Kolibri for production server mode
ENV KOLIBRI_RUN_MODE=prod
ENV KOLIBRI_LISTEN_ADDRESS=0.0.0.0

# Tell Kolibri to serve zip content (Flexbooks, HTML5 apps) through the SAME
# origin as the main server (nginx on port 8080/443).
# Without this, Kolibri tries to use port 8081 which Render blocks.
# Set this to your actual Render URL (no trailing slash).
ENV KOLIBRI_ZIP_CONTENT_ORIGIN=https://lms-online-qvbg.onrender.com

# Render exposes only one port — nginx listens here and proxies internally
ENV PORT=8080
EXPOSE 8080

# Start supervisor which manages both nginx and kolibri
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
