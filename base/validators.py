from urllib.parse import urlparse

from django.core.exceptions import ValidationError


ALLOWED_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
}


def validate_youtube_url(value):
    parsed = urlparse((value or "").strip())
    host = (parsed.netloc or "").lower()

    if parsed.scheme not in {"http", "https"} or host not in ALLOWED_YOUTUBE_HOSTS:
        raise ValidationError("video_url must be a valid YouTube URL.")

    has_video_reference = bool(parsed.path.strip("/")) or bool(parsed.query)
    if not has_video_reference:
        raise ValidationError("video_url must point to a specific YouTube resource.")