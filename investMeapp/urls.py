from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('', views.investment, name='investment'),
    path('manage_members/', views.manage_members, name='manage_members'),
    path('delete_member/<int:member_id>/', views.delete_member, name='delete_member'),
    path('update_investment/<int:investment_id>/', views.update_investment, name='update_investment'),
    path('update_roi/', views.update_roi, name='update_roi'),
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
