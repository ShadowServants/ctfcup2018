FROM php:alpine
LABEL maintainer="alagunto_with_love <priah@mail.ru>"

RUN apk update && apk upgrade && apk add bash git

RUN touch /tmp/main.db

WORKDIR /var/www

CMD php /var/www/artisan migrate && cd /var/www/public && php -S 0.0.0.0:9000
EXPOSE 9000
