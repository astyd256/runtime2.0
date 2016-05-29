
def register(name, manager_class):
    globals()[name] = manager_class()


def has(name):
    return name in globals()[name]
