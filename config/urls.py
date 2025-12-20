# Настройка главного роутера
from django.contrib import admin
from django.urls import path, include, re_path
from users.urls import urlpatterns as users_urls
from storage.urls import urlpatterns as storage_urls
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def debug_urls(request):
    from django.urls.resolvers import get_resolver
    resolver = get_resolver()
    return JsonResponse({
        'urls': [str(p) for p in resolver.url_patterns]
    })

def health_check(request):
    return JsonResponse({"status": "OK", "service": "Cloud Storage Backend"})

def home(request):
    return JsonResponse({"message": "Welcome to the Cloud Storage API!"})

urlpatterns = [
    path('health/', health_check, name='health-check'),  # для отладки и мониторинга
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/auth/', include(users_urls)),
    path('api/storage/', include(storage_urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

urlpatterns += [
    re_path(r'^(?!api/|admin/|static/|storage/|health/).*',
            TemplateView.as_view(template_name='index.html'))
]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
