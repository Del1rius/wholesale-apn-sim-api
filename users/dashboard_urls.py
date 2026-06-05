from django.urls import path
from django.contrib.auth import views as auth_views
from users import dashboard_views

urlpatterns = [
    path(
        'login/',
        dashboard_views.login_view,
        name='login'),
    path(
        'logout/',
        dashboard_views.logout_view,
        name='logout'),
    path(
        'dashboard/',
        dashboard_views.dashboard_view,
        name='dashboard'),
    path(
        'sims/',
        dashboard_views.sim_list_view,
        name='sim_list'),
    path(
        'sims/<str:iccid>/',
        dashboard_views.sim_detail_view,
        name='sim_detail'),
    path(
        'password-change/',
        auth_views.PasswordChangeView.as_view(
            template_name='password_change.html'),
        name='password_change'),
    path(
        'password-change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='password_change_done.html'),
        name='password_change_done'),
]
