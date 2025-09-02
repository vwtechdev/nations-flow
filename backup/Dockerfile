FROM alpine:3.19

RUN apk add --no-cache postgresql-client rclone bash coreutils tzdata

WORKDIR /app

COPY backup.sh /app/backup.sh
COPY crontab.txt /app/crontab.txt

RUN chmod +x /app/backup.sh

CMD ["sh", "-c", "crontab /app/crontab.txt && crond -f -d 8"]