from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('courses/', include('courses.urls')),
    path('schedule/', include('schedule.urls')),
    path('attendance/', include('attendance.urls')),
    path('normativ/', include('normativ.urls')),
    path('coins/', include('coins.urls')),
    path('news/', include('news.urls')),
    path('api/', include('config.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
