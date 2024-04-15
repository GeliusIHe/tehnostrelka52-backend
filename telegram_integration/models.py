from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class TelegramLink(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_chat_id = models.CharField(max_length=255, blank=True, null=True)
    confirmation_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def is_confirmation_code_expired(self):
        expired_time = self.timestamp + timezone.timedelta(minutes=10)
        return timezone.now() > expired_time
