
import managers
from .auxiliary import section, show, confirm, search
from .auxiliary.constants import GROUP


def explain(name, value):
    if isinstance(value, bool):
        return "yes" if value else "no"
    elif isinstance(value, (tuple, list)):
        return ", ".join(value) if value else "<empty>"
    else:
        return value or "<empty>"


def recognize(query):
    identifiers = tuple(part.strip() for part in query.split(","))
    objects = []
    for identifier in identifiers:
        entity, user_or_group = search(user=identifier, group=identifier)
        if user_or_group:
            objects.append((entity, user_or_group))
    return objects


def run(group=None, create=False, system=False, delete=False, description=None, include=None, exclude=None):
    """
    show group information
    :param group: specifies group
    :param switch create: create new group
    :param switch system: force creation of system group
    :param switch delete: delete group
    :param description: group description to set
    :param include: add member(s) to group
    :param exclude: remove member(s) from group
    """
    if group is None:
        with section("available groups"):
            for item in managers.user_manager.get_all_groups():
                show(item.login)
        return

    if create:
        if managers.user_manager.name_exists(group):
            show("user or group with such identifier already exists")
            return
        show("create group %s" % group)
        group = managers.user_manager.create_group(group, system=system, descr=description or "")
        managers.user_manager.sync()
    else:
        entity, group = search(group=group)
        if entity is not GROUP:
            show("no group with such identifier")
            return

    if not (create or delete) and description is None and include is None and exclude is None:
        with section("group %s" % group.login):
            for name in ("id", "login", "description", "members", ("membership", "member_of"), "system"):
                if isinstance(name, tuple):
                    caption, name = name
                else:
                    caption = name.replace("_", " ")
                show(caption, explain(name, getattr(group, name)))
        return

    if description is not None and not create:
        show("update group description")
        group.description = description.strip()
        managers.user_manager.sync()

    if include:
        objects = recognize(include)
        if not objects:
            show("no user(s) or group(s) to include")
            return

        with section("include into group %s" % group.login):
            for entity, user_or_group in objects:
                show("%s %s" % (entity, user_or_group.login))
                group.members.append(user_or_group.login)
        managers.user_manager.sync()

    if exclude:
        objects = [(entity, user_or_group) for entity, user_or_group in recognize(exclude)
            if user_or_group.login in group.members]
        if not objects:
            show("no user(s) or group(s) to include")
            return

        with section("exclude from group %s" % group.login):
            for entity, user_or_group in objects:
                show("%s %s" % (entity, user_or_group.login))
                group.members.remove(user_or_group.login)
        managers.user_manager.sync()

    if delete and confirm(question="delete group %s" % group.login):
        show("delete group %s" % group.login)
        managers.user_manager.remove_user(group.login)
        managers.user_manager.sync()
