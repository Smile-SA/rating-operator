#!/bin/sh

#shellcheck disable=SC2016
envsubst '$PROXIED_API_URL $PROXIED_FRONTEND_URL' \
    </config-proxy/nginx.conf.tpl \
    >/etc/nginx/rating-nginx.conf

nginx -c /etc/nginx/rating-nginx.conf -g "daemon off;"
