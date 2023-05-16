from django.core.exceptions import ValidationError

MAX_FILE_SIZE = 3000000


def validate_products(value):
    """Validate products uploaded file"""
    for product in value:
        files = product.get('uploaded_files')
    return value


def validate_file_size(value):
    filesize = value.size

    if filesize > MAX_FILE_SIZE:
        raise ValidationError("You cannot upload file more than 3Mb")
    else:
        return value
