from rest_framework import permissions, filters
from utils.permissions import AuthorOrReadOnly

from django_filters import rest_framework

import uuid
import logging
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models

logger = logging.getLogger(__name__)

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
    def resize(self, image_field: models.ImageField, percentage: int = 0.5):
        try:
            im = Image.open(image_field)
            width, height = im.size
            mime_type = im.format

            source_image = im.convert('RGB')
            resized_dimensions = (int(width * percentage), int(height * percentage))
            source_image.thumbnail(resized_dimensions)
            output = BytesIO()
            source_image.save(output, format='JPEG')
            output.seek(0)

            content_file = ContentFile(output.read())
            file = File(content_file)

            random_name = f'{uuid.uuid4()}.jpeg'
            image_field.save(random_name, file, save=False)

            return width, height, mime_type
        except Exception as e:
            logger.error(f'Failed to resize image {str(e)}')

    # def resize_by_percentage(image, outfile, percentage):
    #     with Image.open (image) as im:
    #         width, height = im.size
    #         resized_dimensions = (int(width * percentage), int(height * percentage))
    #         resized = im.resize(resized_dimensions)
    #         resized.save(outfile)