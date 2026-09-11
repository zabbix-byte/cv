# Production image — no Chrome/Selenium (CV site only)
FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=4000

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/
RUN chmod +x bin/start.sh

CMD ["sh", "bin/start.sh"]
