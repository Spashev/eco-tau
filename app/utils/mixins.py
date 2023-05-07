from rest_framework import permissions, filters
from utils.permissions import AuthorOrReadOnly

from django_filters import rest_framework

import uuid
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models


class UserQuerySetMixin:
    user_filed = 'user'
    allow_staff_view = False

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        lookup_data = {self.user_filed: user}
        qs = super().get_queryset(*args, **kwargs)
        if not self.allow_staff_view and not user.is_staff:
            return qs
        return qs.filter(**lookup_data)


class ResizeImageMixin:
    def resize(self, image_field: models.ImageField, size: tuple):
        im = Image.open(image_field)
        width, height = im.size
        mime_type = im.format

        source_image = im.convert('RGB')
        source_image.thumbnail(size)
        output = BytesIO()
        source_image.save(output, format='JPEG')
        output.seek(0)

        content_file = ContentFile(output.read())
        file = File(content_file)

        random_name = f'{uuid.uuid4()}.jpeg'
        image_field.save(random_name, file, save=False)

        return width, height, mime_type
