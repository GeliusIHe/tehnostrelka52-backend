from django.http import JsonResponse
from .models import TelegramLink
from django.utils import timezone

def generate_telegram_link(request):
    if request.user.is_authenticated:
        link, created = TelegramLink.objects.update_or_create(
            user=request.user,
            defaults={'timestamp': timezone.now()}
        )
        bot_username = 'tehnostrelkacase5213_bot'
        link_url = f'https://t.me/{bot_username}?start={link.code}'
        return JsonResponse({'link': link_url})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)