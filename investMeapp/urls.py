from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "investmeapp"
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    # path('login/', views.login, name='login'),
    path('investment/', views.investment, name='investment'),
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('request_withdrawal/', views.request_withdrawal, name='request_withdrawal'),
    path('manage_members/', views.manage_members, name='manage_members'),
    path('delete_member/<int:member_id>/', views.delete_member, name='delete_member'),
    path('update_investment/<int:investment_id>/', views.update_investment, name='update_investment'),
    path('update_roi/', views.update_roi, name='update_roi'),
    path('manage_withdrawals/', views.manage_withdrawals, name='manage_withdrawals'),
    path('approve_withdrawal/<int:withdrawal_id>/', views.approve_withdrawal, name='approve_withdrawal'),
    path('paystack-webhook/', views.paystack_webhook, name='paystack_webhook'),

]
