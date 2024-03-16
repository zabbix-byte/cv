class Education:
    def __init__(self,
                 id: int,
                 name: str,
                 entity: str = None
                 ) -> None:
        self.id = id
        self.name = name
        self.entity = entity
        self.time_start = None
        self.time_end = None

    def set_time(self, time: str):
        elements = time.split('-')

        if len(elements) == 2:
            self.time_start = elements[0].strip()
            self.time_end = elements[1].strip()
            