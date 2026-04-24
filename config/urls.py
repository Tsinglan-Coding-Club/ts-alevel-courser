"""
URL configuration for config project.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve


def healthz(_request):
    """Lightweight container health check endpoint."""
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz/', healthz, name='healthz'),
    path('', include('pastpaper.urls')),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    media_prefix = settings.MEDIA_URL.lstrip('/').rstrip('/')
    if media_prefix:
        urlpatterns += [
            re_path(
                rf'^{media_prefix}/(?P<path>.*)$',
                serve,
                {'document_root': settings.MEDIA_ROOT},
            )
        ]
