# syntax=docker/dockerfile:1
FROM python:3.10-bullseye

RUN apt-get update

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

RUN apt-get install -y unzip xvfb libxi6 libgconf-2-4 jq libjq1 libonig5 libxkbcommon0 libxss1 libglib2.0-0 libnss3 \
    libfontconfig1 libatk-bridge2.0-0 libatspi2.0-0 libgtk-3-0 libpango-1.0-0 libgdk-pixbuf2.0-0 libxcomposite1 \
    libxcursor1 libxdamage1 libxtst6 libappindicator3-1 libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libxfixes3 \
    libdbus-1-3 libexpat1 libgcc1 libnspr4 libgbm1 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxext6 \
    libxrandr2 libxrender1 gconf-service ca-certificates fonts-liberation libappindicator1 lsb-release xdg-utils

# Install latest Chrome
RUN CHROME_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chrome[] | select(.platform == "linux64") | .url') \
    && curl -sSLf --retry 3 --output /tmp/chrome-linux64.zip "$CHROME_URL" \
    && unzip /tmp/chrome-linux64.zip -d /opt \
    && ln -s /opt/chrome-linux64/chrome /usr/local/bin/chrome \
    && rm /tmp/chrome-linux64.zip

# Install latest chromedriver
RUN CHROMEDRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform == "linux64") | .url') \
    && curl -sSLf --retry 3 --output /tmp/chromedriver-linux64.zip "$CHROMEDRIVER_URL" \
    && unzip -o /tmp/chromedriver-linux64.zip -d /tmp \
    && rm -rf /tmp/chromedriver-linux64.zip \
    && mv -f /tmp/chromedriver-linux64/chromedriver "/usr/local/bin/chromedriver" \
    && chmod +x "/usr/local/bin/chromedriver"

CMD ["sh", "bin/init_container.sh"]