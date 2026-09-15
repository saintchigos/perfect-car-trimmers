"""Shared validators for user-uploaded images.

The booking form is public and unauthenticated, so damage_photo is the
single biggest attack surface in this project — anyone on the internet can
POST to /book/. These validators make sure whatever lands on disk is
actually a small, genuine image file, not an arbitrarily large file or a
disguised script.
"""
from django.core.exceptions import ValidationError

MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def validate_image_upload(file):
    # 1. Size cap — cheap check, do it first.
    if file.size > MAX_UPLOAD_SIZE_BYTES:
        raise ValidationError("Image is too large — please upload a photo under 5MB.")

    # 2. Extension allow-list.
    name = getattr(file, 'name', '') or ''
    ext = ('.' + name.rsplit('.', 1)[-1].lower()) if '.' in name else ''
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Unsupported file type — please upload a JPG, PNG, or WEBP image.")

    # 3. Actually decode it as an image (blocks disguised/renamed non-image
    #    files, e.g. a .jpg that's really an HTML or script payload).
    try:
        from PIL import Image
        file.seek(0)
        with Image.open(file) as img:
            img.verify()
    except Exception:
        raise ValidationError("This doesn't look like a valid image file — please try a different photo.")
    finally:
        file.seek(0)
