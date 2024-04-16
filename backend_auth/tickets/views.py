from rest_framework import generics, permissions
from backend_auth.models import Ticket, Message
from backend_auth.serializers import TicketSerializer, MessageSerializer
from backend_auth.permissions import IsOwnerOrIsSupportStaff


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

        if self.request.user.profile.role.name == 'support':
            ticket = message.ticket
            ticket.status = 'pending'
            ticket.save()



class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrIsSupportStaff]

    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        return Message.objects.filter(ticket_id=ticket_id)
