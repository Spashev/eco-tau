from datetime import date
from rest_framework import serializers

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


def validate_date_of_birth_manager(value):
    if value > date.today():
        raise serializers.ValidationError("Date of birth cannot be in the future.")

    age = (date.today() - value).days // 365
    if age <= 18:
        raise serializers.ValidationError("You must be at least or equal 18 years old to register.")


def validate_date_of_birth_user(value):
    if value > date.today():
        raise serializers.ValidationError("Date of birth cannot be in the future.")

    age = (date.today() - value).days // 365
    if age <= 16:
        raise serializers.ValidationError("You must be at least or equal 16 years old to register.")
