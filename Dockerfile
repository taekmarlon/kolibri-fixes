FROM python:3.11-slim

# Install Node.js, pnpm, and gettext (required for Kolibri i18n builds)
RUN apt-get update && apt-get install -y curl gettext
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g pnpm

# Set up working directory
WORKDIR /app
COPY . /app

# Install Python dependencies for Kolibri
ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.16.0
RUN mkdir -p kolibri/dist && touch kolibri/dist/__init__.py
RUN pip install -e .

# Install frontend dependencies and build Kolibri frontend
RUN pnpm install
RUN pnpm run build

# Configure Kolibri for production server mode
ENV KOLIBRI_RUN_MODE=prod
ENV KOLIBRI_LISTEN_ADDRESS=0.0.0.0

# Render dynamically assigns the PORT environment variable
ENV PORT=8080
EXPOSE $PORT

# Start Kolibri in the foreground on Render's required port
CMD kolibri start --port=$PORT --foreground
