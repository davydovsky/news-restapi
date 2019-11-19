class ValidationError(Exception):
    status_code = 400


class NotFoundError(Exception):
    status_code = 404

    def __init__(self):
        super().__init__('Not found')
