class AIAdapter:
    def validate_request(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def normalize_response(self):
        raise NotImplementedError

    def health_check(self):
        raise NotImplementedError
