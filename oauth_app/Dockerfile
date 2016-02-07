FROM python:3.3
MAINTAINER Gyorgy Demarcsek

# Add application root
ADD /app /usr/src/app

# Install package dependencies
RUN apt-get update
RUN apt-get install -y nano tar curl net-tools build-essential git nginx-full
RUN pip install --upgrade pip

# Install Python dependencies
WORKDIR /usr/src/app
RUN pip install --default-timeout=200 -r requirements.txt
RUN pip install uwsgi

# Install default certificates
COPY /pki/certs/oauth_app.crt /etc/nginx/ssl/
COPY /pki/certs/oauth_app.key /etc/nginx/ssl/

# Install default configuration
COPY /config/nginx.conf /etc/nginx/sites-available/oauth_app
COPY /config/oauth_providers.cfg /usr/src/app/config.cfg
COPY /entrypoint.sh /entrypoint.sh
RUN ln -s /etc/nginx/sites-available/oauth_app /etc/nginx/sites-enabled/oauth_app
COPY /config/uwsgi.ini /etc/uwsgi.ini
COPY /pki/certs/*.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Create data directory for application
RUN mkdir -p /www-data
RUN chown www-data.www-data /www-data

# Expose ports
EXPOSE 80
EXPOSE 443

# Run application
CMD /entrypoint.sh $UWSGI_EXTRA_PARAMS
