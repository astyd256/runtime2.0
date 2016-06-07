
def register(name, manager_class):
    globals()[name] = manager_class()


def has(*names):
    namespace = globals()
    for name in names:
        if name not in namespace:
            return False
    return True
