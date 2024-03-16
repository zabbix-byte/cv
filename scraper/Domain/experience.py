class Experience:
    def __init__(self,
                 id: int,
                 name: str,
                 time: str = None,
                 description: str = None) -> None:
        self.name = name
        self.time = time
        self.id = id
        self.description = description
        self.group = []

    def serrialize_groups(self):
        for i in range(len(self.group)):
            if type(self.group[i]) == dict:
                continue
            self.group[i] = self.group[i].__dict__
