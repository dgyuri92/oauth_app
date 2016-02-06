FROM gitlab/gitlab-ce:latest
COPY /pki/certs/gitlab.crt /etc/gitlab/ssl/
COPY /pki/certs/gitlab.key /etc/gitlab/ssl/
COPY /gitlab.rb /etc/gitlab/gitlab.rb
COPY /pki/certs/*.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates
