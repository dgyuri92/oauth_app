FROM python:3.3
MAINTAINER Gyorgy Demarcsek
ADD /app /usr/src/app
RUN apt-get update
RUN apt-get install -y nano tar curl net-tools build-essential git nginx-full
RUN pip install --upgrade pip
EXPOSE 80
WORKDIR /usr/src/app
RUN pip install --default-timeout=200 -r requirements.txt
RUN pip install uwsgi
COPY /pki/certs/oauth_app.crt /etc/nginx/ssl/
COPY /pki/certs/oauth_app.key /etc/nginx/ssl/
COPY /config/nginx.conf /etc/nginx/sites-available/oauth_app
COPY /config/oauth_providers.cfg /usr/src/app/config.cfg
COPY /entrypoint.sh /entrypoint.sh
RUN ln -s /etc/nginx/sites-available/oauth_app /etc/nginx/sites-enabled/oauth_app
COPY /config/uwsgi.ini /etc/uwsgi.ini
EXPOSE 443
COPY /pki/certs/*.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates
RUN mkdir -p /www-data
RUN chown www-data.www-data /www-data
CMD /entrypoint.sh $UWSGI_EXTRA_PARAMS
