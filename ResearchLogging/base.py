class ResearchLogger:
    def create_event(self):
        raise NotImplementedError

    def append(self):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError

    def export(self):
        raise NotImplementedError
