from django.db import models
from django.contrib.auth.models import User


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending')
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='tickets', on_delete=models.CASCADE)


class Message(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Media(models.Model):
    ticket = models.ForeignKey('Ticket', related_name='media', on_delete=models.CASCADE)
    file = models.FileField(upload_to='chat_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')

    def __str__(self):
        return f"Media file {self.file.name} uploaded at {self.uploaded_at} for ticket {self.ticket.id}"
