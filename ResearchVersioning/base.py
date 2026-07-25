class ResearchVersionManager:
    def create_snapshot(self):
        raise NotImplementedError

    def load_snapshot(self):
        raise NotImplementedError

    def export(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError
