from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), #pw reset
    path('accounts/', include("allauth.urls")), #allauth
    path("products/", include("market.urls")),  # market
    path('', include('receipts.urls')),
    path("profiles/", include("profiles.urls")), #profiles
    path("ai/", include("market_ai.urls", namespace="market_ai")),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
