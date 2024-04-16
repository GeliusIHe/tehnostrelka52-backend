import requests
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from openai import OpenAI
from django.core.cache import cache

from backend_auth.models import Ticket

import requests


def send_message_to_ticket(user, message_text, ticket_id, token):
    url = "http://localhost:8000/messages/create/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "ticket": ticket_id,
        "text": message_text,
        "author": user.id
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return {"message": "Message successfully created", "data": response.json()}
    else:
        return {"error": "Failed to create message", "status_code": response.status_code, "details": response.text}


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
        token = request.headers.get('Authorization', '').split('Bearer ')[
            -1] if 'Authorization' in request.headers else None
        active_ticket_id = cache.get(f"user_{request.user.id}_active_ticket")
        if active_ticket_id:
            response = send_message_to_ticket(request.user, user_input, active_ticket_id, token)
            return JsonResponse(response, status=status.HTTP_200_OK)

        if not user_input:
            return JsonResponse({'error': 'Message content is required'}, status=status.HTTP_400_BAD_REQUEST)

        if user_input.lower().startswith("оператор"):
            ticket = Ticket.objects.create(
                user=request.user,
                title="Chat Operator Called",
                description="The user has requested to speak with a chat operator."
            )
            cache.set(f"user_{request.user.id}_active_ticket", ticket.id, timeout=3600)  # активировать на час

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
