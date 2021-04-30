from django.core.exceptions import ValidationError


class FileSizeValidator:
    def __init__(self, limit, message):
        self.limit = limit
        self.message = message

    def __call__(self, new_file):
        if new_file.size > self.limit:
            raise ValidationError(self.message)
