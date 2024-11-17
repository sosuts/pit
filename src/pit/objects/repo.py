import os


class Repository:
    def __init__(self, path):
        self.path = path
        self.objects = {}
        self.branches = {}
        self.head = None

    def init(self):
        os.makedirs(self.path, exist_ok=True)
        os.makedirs(os.path.join(self.path, "objects"), exist_ok=True)
        self.head = "master"
        self.branches["master"] = None

    def save_object(self, obj):
        obj_hash = obj.compute_hash()
        self.objects[obj_hash] = obj
        return obj_hash

    def get_object(self, hash):
        return self.objects.get(hash)

    def checkout(self, ref):
        if ref not in self.branches:
            raise ValueError(f"Branch or commit '{ref}' not found.")
        self.head = ref
