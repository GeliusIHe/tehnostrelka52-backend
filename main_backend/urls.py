"""
URL configuration for main_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from backend_auth.authorization.views import LoginView, RegisterView
from backend_auth.chat.views import ChatInitView
from backend_auth.tickets.views import TicketListView, TicketCreateView, MessageCreateView, TicketDetailView, MessageListView, FileUploadView, FileListView
from telegram_integration.views import generate_telegram_link, LinkTelegramAccount
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('tickets/', TicketListView.as_view(), name='ticket-list'),
    path('tickets/create/', TicketCreateView.as_view(), name='ticket-create'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('messages/create/', MessageCreateView.as_view(), name='message-create'),
    path('tickets/<int:ticket_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('generate_link/', generate_telegram_link, name='generate_telegram_link'),
    path('chat/init/', ChatInitView.as_view(), name='chat-init'),
    path('api/link_telegram/', LinkTelegramAccount.as_view(), name='link_telegram_account'),
    path('files/upload/', FileUploadView.as_view(), name='file-upload'),
    path('files/<int:ticket_id>/', FileListView.as_view(), name='file-list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
