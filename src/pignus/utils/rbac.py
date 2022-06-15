"""RBAC
Role Based Access Control Utility

"""

from pignus.models.perm import Perm
from pignus.models.role import Role
from pignus.models.role_perm import RolePerm
from pignus.collections.roles import Roles
from pignus.collections.perms import Perms
from pignus.collections.role_perms import RolePerms
from pignus.utils import log


class Rbac:
    def __init__(self):
        self.default_rbac_layout = {
            "admin": [
                "list-api-keys", "post-api-keys", "delete-api-keys",
                "list-clusters", "post-clusters", "delete-clusters",
                "list-cves",
                "list-image-clusters", "post-image-clusters", "delete-image-clusters",
                "list-images", "post-images", "post-image-auth", "delete-images",
                "list-operations", "delete-operations",
                "list-options", "post-options",
                "list-roles", "post-roles",
                "list-role-perms", "post-role-perms", "delete-roles-perms",
                "list-perms",
                "list-scanners", "post-scanners", "delete-scannners",
                "list-scans",
                "list-users", "post-users", "delete-users",
            ],
            "human": [
                "list-clusters",
                "list-cves",
                "list-image-clusters",
                "list-images",
                "list-operations",
                "list-options",
                "list-perms",
                "list-roles",
                "list-role-perms",
                "list-scans",
                "list-users",
            ],
            "cluster": ["check-in"],
            "image-auth": ["list-images", "post-image-auth"],
        }

    def load_rbak_tree(self) -> dict:
        """Dynamically loads the entire RBAC tree from the database."""
        roles = Roles().get_all()
        perms = Perms().get_all()
        role_perms = RolePerms().get_all()
        ret = {}
        for role in roles:
            ret[role.slug_name] = {}
            for perm in perms:
                for role_perm in role_perms:
                    if role_perm.role_id == role.id and role_perm.perm_id == perm.id:
                        ret[role.slug_name][perm.slug_name] = True
        return ret

    def get_role_perms(self, role_id: int, simplified=True) -> list:
        """Get all permissions for a Role by the Role.id, returning a list of Perm slug names.
        """
        role_perms = RolePerms().get_by_role_id(role_id)

        if not role_perms:
            return []

        perm_ids = []
        for role_perm in role_perms:
            if not role_perm.enabled:
                continue
            perm_ids.append(role_perm.perm_id)

        if not perm_ids:
            return []

        perms = Perms().get_by_ids(perm_ids)

        if not simplified:
            return perms

        perm_slugs = []
        for perm in perms:
            perm_slugs.append(perm.slug_name)

        return perm_slugs

    def check_perm_by_role_id(self, perm_slug: str, role_id: int) -> bool:
        """RBAC auth check of a perm_slug for a given role_id. """
        perm = Perm()
        # If we can't find the Perm by slug, deny.
        if not perm.get_by_slug(perm_slug):
            log.warning('RBAC Denied: No Perm slug "%s"' % perm_slug)
            return False

        role = Role()
        #  If we can't find the Role by ID, deny.
        if not role.get_by_id(role_id):
            log.warning('RBAC Denied: No Role ID "%s"' % role_id)
            return False

        role_perm = RolePerm()
        if not role_perm.get_by_role_perm(role.id, perm.id):
            log.warning('RBAC Denied: No RolePerm by Role ID: "%s" and Perm ID: "%s" enabled.' % (
                role.id, perm.id))
            return False
        log.debug('RBAC Allowed: Role %s and Perm %s.' % (role, perm))
        return True

    def create_default_rbac_layout(self) -> bool:
        """Creates the RBAC layout defined  by self.default_rbac_layout. """
        for role_slug, perm_slugs in self.default_rbac_layout.items():
            role = self.create_role(role_slug, role_slug)
            for perm_slug in perm_slugs:
                perm = self.create_perm(perm_slug, perm_slug)
                role_perm = RolePerm()
                if not role_perm.get_by_role_perm(role.id, perm.id):
                    role_perm.role_id = role.id
                    role_perm.perm_id = perm.id
                    role_perm.save()
                    log.info("Created Role Perm binding %s - %s" % (role.name, perm.name))
        return True

    def create_perm(self, perm_name: str, perm_slug_name: str):
        """Safely create a Perm if it doesn't already exist by the slug_name, returning back the
        Perm object.
        """
        perm = Perm()
        if perm.get_by_slug(perm_slug_name):
            return perm
        perm.name = perm_name
        perm.slug_name = perm_slug_name
        perm.save()
        return perm

    def create_role(self, role_name: str, role_slug_name: str):
        """Safely create a Role if it doesn't already exist by the slug_name, returning back the
        Role object.
        """
        role = Role()
        if role.get_by_slug(role_slug_name):
            return role
        role.name = role_name
        role.slug_name = role_slug_name
        role.save()
        return role

# End File: automox/pignus/src/pignus/utils/rbac.py
