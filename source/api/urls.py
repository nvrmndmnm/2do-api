from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'todo', views.TaskViewSet)

app_name = 'api'

urlpatterns = [
    path("", include(router.urls)),
    path('auth/login/', views.LoginView.as_view(), name='login'),
]
