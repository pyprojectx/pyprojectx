def initialize(template):
    return locals()[f"initialize_{template}"]()


def initialize_global():
    pass
