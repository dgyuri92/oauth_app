nginx['redirect_http_to_https'] = false
nginx['ssl_certificate'] = "/etc/gitlab/ssl/#{node['fqdn']}.crt"
nginx['ssl_certificate_key'] = "/etc/gitlab/ssl/#{node['fqdn']}.key"
nginx['listen_https'] = true # override only if your reverse proxy internally communicates over HTTP: https://gitlab.com/gitlab-org/omnibus-gitlab/blob/master/doc/settings/nginx.md#supporting-proxied-ssl
