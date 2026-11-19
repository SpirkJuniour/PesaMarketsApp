from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('markets.urls')),
]

handler404 = 'markets.views.custom_404'
handler500 = 'markets.views.custom_500'
