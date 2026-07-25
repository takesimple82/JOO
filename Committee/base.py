class Committee:
    def prepare(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    def export(self):
        raise NotImplementedError
