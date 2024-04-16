import telebot
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from backend_auth.models import Ticket, Message, Media
from backend_auth.permissions import IsOwnerOrIsSupportStaff
from backend_auth.serializers import TicketSerializer, MessageSerializer, MediaSerializer
from telegram_integration.models import TelegramLink

TOKEN = '7046099150:AAE39SRoCZ6NzOS0cQs-UbC2S7p2J03J3mA'
bot = telebot.TeleBot(TOKEN)


class TicketListView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrIsSupportStaff]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.role.name == 'support':
            return Ticket.objects.all()  #
        return Ticket.objects.filter(user=user)


class TicketDetailView(generics.RetrieveAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrIsSupportStaff]


class TicketCreateView(generics.CreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        message = serializer.save(author=self.request.user)
        ticket = message.ticket

        if self.request.user.profile.role.name == 'support':
            ticket.status = 'pending'
            ticket.save()

            try:
                telegram_link = TelegramLink.objects.get(user=ticket.user)
                if telegram_link and telegram_link.telegram_chat_id:
                    message_text = f"На ваш тикет №{ticket.id} поступил ответ от техподдержки."
                    bot.send_message(chat_id=telegram_link.telegram_chat_id, text=message_text)
            except TelegramLink.DoesNotExist:
                print(f"No Telegram link found for user {ticket.user.username}")
            except Exception as e:
                print(f"Failed to send Telegram message: {str(e)}")


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrIsSupportStaff]

    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        return Message.objects.filter(ticket_id=ticket_id)


class FileUploadView(generics.CreateAPIView):
    serializer_class = MediaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ticket_id = request.data.get('ticket_id')
        file = request.data.get('file')
        if not file or not ticket_id:
            return Response({"error": "File and ticket_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        ticket = Ticket.objects.filter(id=ticket_id, user=request.user).first()
        if not ticket:
            return Response({"error": "Ticket not found or access denied"}, status=status.HTTP_404_NOT_FOUND)

        media = Media.objects.create(ticket=ticket, file=file, user=request.user)
        return Response({"message": "File uploaded successfully", "media_id": media.id}, status=status.HTTP_201_CREATED)

class FileListView(generics.ListAPIView):
    serializer_class = MediaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        ticket_id = self.kwargs['ticket_id']
        user = self.request.user
        if user.profile.role.name == 'support' or Ticket.objects.filter(id=ticket_id, user=user).exists():
            return Media.objects.filter(ticket_id=ticket_id)
        return Media.objects.none()
