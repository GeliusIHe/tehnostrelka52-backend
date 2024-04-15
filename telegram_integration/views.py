from django.http import JsonResponse
from .models import TelegramLink
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


def generate_telegram_link(request):
    print("Headers Received:", request.headers.get('Authorization'))

    try:
        user_auth = JWTAuthentication().authenticate(request)
        if user_auth is not None:
            request.user, request.auth = user_auth
            print("JWT User:", request.user)
            print("JWT Payload:", request.auth.payload)
        else:
            print("No user_auth returned from JWT authentication.")
    except (InvalidToken, TokenError) as e:
        print("JWT Error:", str(e))
        return JsonResponse({'error': 'Invalid token or token error'}, status=401)

    if request.user and request.user.is_authenticated:
        link, created = TelegramLink.objects.update_or_create(
            user=request.user,
            defaults={'timestamp': timezone.now()}
        )
        bot_username = 'tehnostrelkacase5213_bot'
        confirmation_code_str = str(link.confirmation_code)
        link_url = f'https://t.me/{bot_username}?start={confirmation_code_str}'
        return JsonResponse({'link': link_url})
    else:
        print("Authentication Failed: User not authenticated")
        return JsonResponse({'error': 'User not authenticated'}, status=401)

