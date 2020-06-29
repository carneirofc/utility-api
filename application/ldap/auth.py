import base64
import hashlib
import ldap
import logging
import typing
import random

from flask import make_response, current_app
from application import redis_client
from application.utils import get_logger

logger = get_logger()
logger.setLevel(logging.DEBUG)


def generate_token(data, expire: int = 3600) -> bytes:
    """ Generate token based on the authorization """
    token = hashlib.blake2s(
        data.encode("utf-8"),
        key=current_app.config["SECRET_KEY"].encode("utf-8"),
        salt="{:.4}".format(random.random()).encode("utf-8"),
    ).hexdigest()
    logger.info('Generate token: "{}" from "{}"'.format(token, data))
    redis_client.set(token, data, ex=expire)
    return token


def delete_token(token: bytes):
    logger.info('Delete token: "{}"'.format(token))
    redis_client.delete(token)


def get_from_token(token: bytes, expire: int = 3600):
    user_data = redis_client.get(token)
    if not user_data:
        raise Exception("Token invalid")

    redis_client.expire(token, expire)
    logger.info('Get token: "{}"="{}", expire in {}s'.format(token, user_data, expire))
    return user_data.decode("utf-8")


class Auth:
    def __init__(self, headers):
        # fmt: off
        self.authorization = headers.get("Authorization",       None)
        self.bind_dn       = headers.get("X-Ldap-BindDN",       "cn=admin,dc=lnls,dc=br")
        self.bind_pass     = headers.get("X-Ldap-BindPass",     current_app.config['LDAP_BINDPASS'])
        self.group_base_dn = headers.get("X-Ldap-Group-BaseDN", "")
        self.group_cns     = headers.get("X-Ldap-Group-CNs",    "").split(",")
        self.realm         = headers.get("X-Ldap-Realm",        "Default LDAP Realm")
        self.starttls      = headers.get("X-Ldap-Starttls",     "false")
        self.url           = headers.get("X-Ldap-URL",          "ldap://10.0.38.42:389")
        self.user_base_dn  = headers.get("X-Ldap-User-BaseDN",  "ou=users,dc=lnls,dc=br")
        # fmt: on

    def get_user_pass(self) -> typing.Tuple[str, str]:

        if self.authorization is None:
            raise Exception("No Authorization header!")

        if not self.authorization.lower().startswith("basic "):
            raise Exception("Invalid Authorization header!")

        logger.debug("decoding credentials")

        try:
            auth_decoded = base64.b64decode(self.authorization[6:])
            auth_decoded = auth_decoded.decode("utf-8")
            user, passwd = auth_decoded.split(":", 1)
            return user, passwd

        except:
            raise Exception(
                "Failed to get information from Authorization header. {}".format(
                    self.authorization
                )
            )

    def get_search_user(self, l, user, passw):
        logger.debug("binding as search user")
        l.bind_s(self.bind_dn, self.bind_pass, ldap.AUTH_SIMPLE)

        logger.debug("preparing search filter")
        searchfilter = "(cn={})".format(user)

        logger.debug(
            ('searching on server "%s" with base dn ' + '"%s" with filter "%s"')
            % (self.url, self.user_base_dn, searchfilter)
        )

        logger.info(
            "running user search query {} with filter {}".format(
                self.user_base_dn, searchfilter
            )
        )
        results = l.search_s(
            self.user_base_dn, ldap.SCOPE_SUBTREE, searchfilter, ["objectclass"], 1
        )

        logger.debug("verifying search query results")
        nres = len(results)

        if nres < 1:
            logger.error("no user objects found")
            return None

        if nres > 1:
            logger.warn(
                "note: filter match multiple user objects: %d, using first" % nres
            )

        user_entry = results[0]
        ldap_dn = user_entry[0]

        if ldap_dn == None:
            logger.error("matched object has no dn")
            return None
        return ldap_dn

    def authenticate(self, user, passw):
        try:

            l = ldap.initialize(self.url)
            l.protocol_version = ldap.VERSION3
            l.set_option(ldap.OPT_NETWORK_TIMEOUT, 5.0)

            if self.starttls == "true":
                l.start_tls_s()

            ldap_dn = self.get_search_user(l, user, passw)
            if not ldap_dn:
                return False

            # Check if user in groups
            logger.info(
                'Required groups for user "{}" {}'.format(ldap_dn, self.group_cns)
            )

            # Include check of groups
            for gcn in self.group_cns:

                search_string = "(&(cn={})(member={}))".format(gcn, ldap_dn)

                logger.info(
                    'Group Base DN: "{}" Search String: "{}"'.format(
                        self.group_base_dn, search_string
                    )
                )
                res = l.search_s(
                    self.group_base_dn, ldap.SCOPE_SUBTREE, search_string, ["member"],
                )
                logger.debug(
                    "check if {} is member of {},{}".format(
                        ldap_dn, gcn, self.group_base_dn
                    )
                )
                if "{}".format(ldap_dn).encode("utf-8") not in res[0][1]["member"]:
                    raise Exception("user do not belong to group")

            logger.debug('attempting to bind using dn "%s"' % (ldap_dn))
            l.bind_s(ldap_dn, passw, ldap.AUTH_SIMPLE)

            return True
        except:
            logger.exception("Failed to authenticate")
            return False
