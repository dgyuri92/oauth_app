#!/bin/bash
/usr/sbin/service nginx start && /usr/local/bin/uwsgi --ini /etc/uwsgi.ini "$@"
