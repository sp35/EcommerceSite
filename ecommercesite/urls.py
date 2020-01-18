from django.contrib import admin
from django.urls import path, include
from users import views as users_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/oauth/', include('allauth.urls')),
    path('accounts/signup/', users_views.SignUpView.as_view() , name='signup'),
    path('accounts/signup/vendor/',users_views.VendorSignUpView.as_view() , name='vendor_signup'),
    path('accounts/signup/customer/',users_views.CustomerSignUpView.as_view() , name='customer_signup'),
    path('accounts/update/customer/<int:pk>',users_views.CustomerUpdateView.as_view() , name='customer-update'),
]

#from django doc
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)