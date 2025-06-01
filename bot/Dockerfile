FROM python:3.10-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    chromium \
    supervisor \
    wget \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Configura variáveis de ambiente
ENV DISPLAY=:99

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY . /app

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o arquivo de configuração do supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expõe a porta do VNC
EXPOSE 5900

# Comando de inicialização: cria senha do VNC e inicia supervisord
CMD bash -c "mkdir -p /etc/x11vnc && \
    x11vnc -storepasswd \$VNC_PASSWORD /etc/x11vnc/vncpass && \
    exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf"
