class ResearchReplay:
    def prepare(self):
        raise NotImplementedError

    def replay(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    def export(self):
        raise NotImplementedError
