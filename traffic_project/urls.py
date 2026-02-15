"""traffic_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index.html'),

    # Auth
    path('user-login.html/', views.user_login, name='user_login'),
    path('about.html/', views.about_page, name='about'),
    path('user-signup.html/', views.user_signup, name='user_signup'),
    path('admin-login.html/', views.admin_login, name='admin_login'),
    path('logout/', views.user_logout, name='logout'),
    
    # User Routes
    path('user-login.html/user-dashboard.html', views.user_dashboard, name='user_dashboard'),
    path('user-login.html/upload.html', views.upload_evidence, name='upload'),
    path('user-login.html/violations.html', views.violations_history, name='violations'),
    path('rewards/', views.rewards_page, name='rewards'),
    path('user-login.html/challan.html', views.check_challan, name='check_challan'),
    path('user-login.html/profile.html', views.profile, name='profile'),
    path('user-login.html/fir.html', views.file_fir, name='file_fir'),
    
    # Admin Routes
    path('admin-login.html/admin-dashboard.html', views.admin_dashboard, name='admin_dashboard'),
    path('admin-login.html/admin-dashboard.html/admin-profiles.html', views.admin_profiles, name="admin_profiles"),
    path('admin-login.html/admin-dashboard.html/vehicle-listings.html', views.vehicle_listings, name='vehicle_list'),
     path('admin-login.html/admin-dashboard.html/memo-verification.html', views.memo_verification, name='memo_verification'),
    path('memo-verify/<str:memo_id>/', views.verify_memo, name='verify_memo'),
    path('memo-reject/<str:memo_id>/', views.reject_memo, name='reject_memo'),
     path(
        "admin-login.html/admin-dashboard.html/memo-verification.html/evidence-verification.html/<str:memo_id>",
        views.evidence_verification,
        name="evidence_verification"
    ),
    path(
    'admin-login.html/admin-dashboard.html/boundary-creation.html', views.boundary_creation, name='boundary_creation'
),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)