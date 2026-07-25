class ExecutionEngine:
    def prepare(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError

    def export(self):
        raise NotImplementedError
