from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'api/', include("api.urls")),
    path(r'api/auth/', include('knox.urls')),
    path(r'api/password_reset/', include('django_rest_passwordreset.urls'))
]
