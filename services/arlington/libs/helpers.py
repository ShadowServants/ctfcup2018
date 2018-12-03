class NonObject:
    def __getattr__(self, item):
        return None

    def __getitem__(self, item):
        return None


def optional(obj):
    if obj:
        return obj
    return NonObject()