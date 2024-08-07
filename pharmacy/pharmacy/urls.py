"""
URL configuration for pharmacy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from pharmacy.user import urls as user_urls
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from pharmacy.core import urls as core_urls
from pharmacy.product import urls as product_urls


urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include(user_urls)),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Company
    path("", include(core_urls)),
    path("", include(product_urls)),
]
