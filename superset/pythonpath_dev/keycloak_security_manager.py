import logging
from typing import Any, Dict, Optional

from superset.security import SupersetSecurityManager

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class KeycloakSecurityManager(SupersetSecurityManager):
    def get_oauth_user_info(
            self, provider: str, resp: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # for Keycloak
        if provider in ["keycloak"]:
            log.debug("Keycloak response: %s", resp)

            if 'userinfo' in resp and 'realm_access' in resp['userinfo']:
                data = resp['userinfo']
            else:
                data = self.appbuilder.sm.oauth_remotes[provider].userinfo()

            roles_expected = self.appbuilder.get_app.config["AUTH_ROLES_MAPPING"]
            roles_retrieved = 'roles' in data or ('realm_access' in data and 'roles' in data['realm_access'])
            if roles_expected and not roles_retrieved:
                log.warning('The roles claim was not added to the id_token or to the userinfo by Keycloak. '
                            'Configure the Realm Roles token mapper to add the roles claim to either the id_token '
                            'or to the userinfo (or both) if you want to map Keycloak roles to Superset roles.')

            log.debug("User info from Keycloak: %s", data)

            roles = set()
            if roles_expected and roles_retrieved:
                roles.update(data.get('roles', []))

                if ('realm_access' in data):
                    roles.update(data['realm_access'].get('roles', []))

                log.debug("Roles from Keycloak: %s", roles)

            return {
                "username": data.get("preferred_username", ""),
                "first_name": data.get("given_name", ""),
                "last_name": data.get("family_name", ""),
                "email": data.get("email", ""),
                "role_keys": roles,
            }
        else:
            super(KeycloakSecurityManager, self).get_oauth_user_info(provider, resp)
