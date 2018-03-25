
import managers
from .auxiliary import section, show, warn, confirm, search
from .auxiliary.constants import USER


def explain(name, value):
    if isinstance(value, bool):
        return "yes" if value else "no"
    elif isinstance(value, (tuple, list)):
        return ", ".join(value) if value else "<empty>"
    else:
        return value or "<empty>"


def run(user=None, create=False, system=False, delete=False, password=None, email=None, level=None):
    """
    show user information or change password
    :arg user: specifies user
    :key switch create: create new user
    :key switch system: force creation of system user
    :key switch delete: delete user
    :key password: password to set
    :key email: email to set
    :key level: security level to set
    """
    if user is None:
        with section("available users"):
            for item in managers.user_manager.get_all_users():
                show(item.login)
        return

    if create:
        if managers.user_manager.name_exists(user):
            warn("user or group with such identifier already exists")
            return
        if not password:
            warn("create require user password")
            return
        show("create user %s" % user)
        user = managers.user_manager.create_user(user, password, system=system, email=email or "", slv=level or "")
        managers.user_manager.sync()
    else:
        entity, user = search(user=user)
        if entity is not USER:
            warn("no user with such identifier")
            return

    if not (create or delete) and password is None and email is None and level is None:
        with section("user %s" % user.login):
            for name in ("id", "login", "password", "first_name", "last_name", "security_level", "email", ("membership", "member_of"), "system"):
                if isinstance(name, tuple):
                    caption, name = name
                else:
                    caption = name.replace("_", " ")
                show(caption, explain(name, getattr(user, name)))
        return

    if password and not create:
        show("update user password")
        user.password = password
        managers.user_manager.sync()

    if email and not create:
        show("update user email")
        user.email = email
        managers.user_manager.sync()

    if level and not create:
        show("update user security level")
        user.security_level = level
        managers.user_manager.sync()

    if delete and confirm(question="delete user %s" % user.login):
        show("delete user %s" % user.login)
        managers.user_manager.remove_user(user.login)
        managers.user_manager.sync()
