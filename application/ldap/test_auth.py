#!/usr/bin/env python3
from utils import get_logger
import auth
import base64
import logging


"""
            - ADMIN_PASSWORD=controle
            - CERTIFICATE_PASSWORD=controle
            - DB_USER=lnls_olog_user
            - DB_PASSWORD=controle 
            - DB_NAME=olog 
            - REALM_SEARCH_BIND_DN="cn=admin,dc=lnls,dc=br"
            - REALM_SEARCH_BIND_PASS="***REMOVED***"
            - REALM_SEARCH_FILTER="cn=%s"
            - REALM_BASE_DN="ou=users,dc=lnls,dc=br"
            - REALM_GROUP_DN="ou=olog,ou=groups,dc=lnls,dc=br"
            - REALM_GROUP_FILTER="(&(objectClass=groupOfNames)(member=%d))"
            - REALM_URL="ldap://10.0.38.42:389"
"""
if __name__ == "__main__":
    headers_olog = {
        "X-Ldap-BindPass": "***REMOVED***",
        "X-Ldap-Group-BaseDN": "ou=olog,ou=groups,dc=lnls,dc=br",
        "X-Ldap-Group-CNs": "olog-admins,olog-logbooks,olog-logs,olog-tags",
    }

    headers_archiver = {
        "X-Ldap-BindPass": "***REMOVED***",
        "X-Ldap-Group-BaseDN": "ou=epics-archiver,ou=groups,dc=lnls,dc=br",
        "X-Ldap-Group-CNs": "archiver-admins",
    }

    a = auth.Auth(headers_archiver)
    a.authenticate("claudio.carneiro", "carneiro")
