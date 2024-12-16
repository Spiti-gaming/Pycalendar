FROM python:3.9

WORKDIR /app

COPY index.py .
COPY requirements.txt .
COPY api.py .


RUN mkdir "ical"



RUN pip install -r requirements.txt
RUN apt-get update && apt-get -y install cron

COPY cron.sh .
COPY /cron/cronfile /etc/cron.d/cronfile

COPY entrypoint.sh /entrypoint.sh
RUN chmod 0644 /etc/cron.d/cronfile

# Appliquer le fichier cron
RUN crontab /etc/cron.d/cronfile


RUN chmod +x /entrypoint.sh
RUN chmod +x index.py
RUN chmod +x cron.sh


ENTRYPOINT ["/entrypoint.sh"]