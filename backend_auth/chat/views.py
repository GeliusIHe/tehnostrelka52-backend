from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from openai import OpenAI

from backend_auth.models import Ticket


class ChatInitView(APIView):
    authentication_classes = []

    def post(self, request):
        print("Headers Received:", request.headers.get('Authorization'))

        try:
            user_auth = JWTAuthentication().authenticate(request)
            if user_auth is not None:
                request.user, request.auth = user_auth
                print("JWT User:", request.user.username)
                print("JWT Payload:", request.auth.payload)
            else:
                print("No user_auth returned from JWT authentication.")
                return JsonResponse({'error': 'Authentication failed'}, status=status.HTTP_401_UNAUTHORIZED)
        except (InvalidToken, TokenError) as e:
            print("JWT Error:", str(e))
            return JsonResponse({'error': 'Invalid token or token error'}, status=status.HTTP_401_UNAUTHORIZED)

        if not request.user.is_authenticated:
            print("Authentication Failed: User not authenticated")
            return JsonResponse({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        user_input = request.data.get('message')
        if not user_input:
            return JsonResponse({'error': 'Message content is required'}, status=status.HTTP_400_BAD_REQUEST)

        if user_input.lower() == "оператор":
            ticket = Ticket.objects.create(user=request.user)
            return JsonResponse(
                {'message': f'Ticket {ticket.id} created successfully. A support staff will be with you shortly.'},
                status=status.HTTP_201_CREATED)

        client = OpenAI(api_key='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')

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant designed to output responses in a specific JSON format. "
                            "Please ensure each response includes a 'messageContent' field for the message text, "
                            "and up to three button fields formatted as 'button1', 'button2', 'button3', "
                            "each containing a 'content' attribute describing the button's purpose."},
                {"role": "user", "content": user_input}
            ]
        )

        if response.choices:
            bot_response = response.choices[0].message.content
        else:
            bot_response = 'No response from bot'
        return JsonResponse({'message': bot_response}, status=status.HTTP_200_OK)