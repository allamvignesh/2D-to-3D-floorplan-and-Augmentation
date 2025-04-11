from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', include("upload.urls")),
    path('', include("upload.urls"))
] + static(settings.MODELS_URL, document_root=settings.MODELS_ROOT)