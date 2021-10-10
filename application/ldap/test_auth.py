#!/usr/bin/env python3
import auth

if __name__ == "__main__":
    headers_olog = {
        "X-Ldap-BindPass": "",
        "X-Ldap-Group-BaseDN": "ou=olog,ou=groups,dc=lnls,dc=br",
        "X-Ldap-Group-CNs": "olog-admins,olog-logbooks,olog-logs,olog-tags",
    }

    headers_archiver = {
        "X-Ldap-BindPass": "",
        "X-Ldap-Group-BaseDN": "ou=epics-archiver,ou=groups,dc=lnls,dc=br",
        "X-Ldap-Group-CNs": "archiver-admins",
    }

    a = auth.Auth(headers_archiver)
    a.authenticate("", "")
