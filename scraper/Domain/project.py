class Project:
    def __init__(self,
                 id: int,
                 name: str,
                 time: str = None,
                 description: str = None
                 ) -> None:
        self.id = id
        self.name = name
        self.time = time
        self.description = description
