#!/bin/sh
set -exu

cat > ./envvars << EOF
SECRET_KEY=${SECRET_KEY}
REDIS_URL=${REDIS_URL}
LDAP_BINDPASS=${LDAP_BINDPASS}
SPREADSHEET_XLSX_PATH=${SPREADSHEET_XLSX_PATH}
SPREADSHEET_SOCKET_PATH=${SPREADSHEET_SOCKET_PATH}
EOF

mod_wsgi-express start-server wsgi.py \
    --port=80 \
    --user www-data\
    --group www-data\
    --log-to-terminal\
    --envvars-script ./envvars
