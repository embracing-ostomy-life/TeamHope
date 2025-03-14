import logging
import os
import secrets
from io import BytesIO

from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

PICTURE_WIDTH = 100
PICTURE_HEIGHT = 100

# Create the logger
logger = logging.getLogger(__name__)


def process_profile_picture(image_file, dimensions=None):
    """

    """
    picture_extensions = [".png", ".jpeg", ".jpg", ".svg"]
    _, ext = os.path.splitext(image_file.name)

    if ext.lower() not in picture_extensions:
        logger.error(f"Wrong Picture extension! Allowed extensions are: {picture_extensions}")
        raise ValidationError(
            f"Wrong Picture extension! Allowed extensions are: {picture_extensions}"
        )
    if not dimensions:
        dimensions = (PICTURE_WIDTH, PICTURE_HEIGHT)
    filename = f"{secrets.token_hex(8)}{ext.lower()}"

    try:
        thumb = Image.open(image_file)
        thumb.thumbnail(size=dimensions)
        thumb_io = BytesIO()
        thumb.save(thumb_io, format="JPEG")
        thumb_file = InMemoryUploadedFile(
            file=thumb_io,
            field_name=None,
            name=filename,
            content_type=image_file.content_type,
            size=dimensions,
            charset=None
        )
        return thumb_file
    except FileNotFoundError:
        logger.error(f"Picture file not found: {image_file}")
        return None
