from django.db import models
from django.contrib.auth.models import User

class TelegramLink(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_link')
    uuid = models.UUIDField(unique=True, db_index=True)
    telegram_id = models.CharField(max_length=128, unique=True, null=True, blank=True)

    def __str__(self):
        return f"User {self.user.username} linked with UUID {self.uuid}"
