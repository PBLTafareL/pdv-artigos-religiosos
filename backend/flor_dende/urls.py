from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',       include('apps.accounts.urls')),
    path('api/products/',   include('apps.products.urls')),
    path('api/pdv/',        include('apps.pdv.urls')),
    path('api/quotations/', include('apps.quotations.urls')),
    path('api/invoices/',   include('apps.invoices.urls')),
    path('api/loyalty/',    include('apps.loyalty.urls')),
    path('api/dashboard/',  include('apps.dashboard.urls')),
    path('api/reports/',    include('apps.reports.urls')),
]

urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
