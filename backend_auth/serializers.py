from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from .models import Ticket, Message, Media
from rest_framework import generics


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'status', 'created_at', 'updated_at', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    role = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'ticket', 'text', 'timestamp', 'author', 'role']

    def get_role(self, obj):
        if hasattr(obj.author, 'profile'):
            return obj.author.profile.role.name
        return None


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file', 'message', 'uploaded_at']


class MediaListView(generics.ListAPIView):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]


class MediaRetrieveView(generics.RetrieveAPIView):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
