"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
]

if settings.DEBUG:
    from django.views.static import serve as _serve

    def _no_cache_serve(request, path, **kwargs):
        response = _serve(request, path, **kwargs)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        try:
            del response['ETag']
        except KeyError:
            pass
        try:
            del response['Last-Modified']
        except KeyError:
            pass
        return response

    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', _no_cache_serve, {
            'document_root': str(settings.BASE_DIR / 'static'),
            'show_indexes': False,
        }),
        re_path(r'^media/(?P<path>.*)$', _no_cache_serve, {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': False,
        }),
    ]
