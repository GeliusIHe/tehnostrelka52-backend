from django.http import JsonResponse
from .models import TelegramLink
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


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


class LinkTelegramAccount(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code")
        chat_id = request.data.get("chat_id")
        if not code or not chat_id:
            return Response({"error": "Code and chat_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            link = TelegramLink.objects.get(confirmation_code=code)
            if link.telegram_chat_id:
                return Response({"error": "This user has already linked a Telegram account."},
                                status=status.HTTP_400_BAD_REQUEST)

            if not link.is_confirmation_code_expired():
                if TelegramLink.objects.filter(telegram_chat_id=chat_id).exists():
                    return Response({"error": "This Telegram account is already linked to another user."},
                                    status=status.HTTP_400_BAD_REQUEST)

                link.telegram_chat_id = chat_id
                link.save()
                return Response({"message": "Account successfully linked"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Code expired"}, status=status.HTTP_400_BAD_REQUEST)
        except TelegramLink.DoesNotExist:
            return Response({"error": "Invalid code"}, status=status.HTTP_404_NOT_FOUND)
