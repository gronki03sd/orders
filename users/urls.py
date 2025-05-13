from django.urls import path
from . import views
app_name = 'users'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('profile/', views.profile, name='profile'),
    path('', views.users_list, name='users-list'),
    path('create/', views.user_create, name='user-create'),
    path('<int:pk>/update/', views.user_update, name='user-update'),
    path('<int:pk>/delete/', views.user_delete, name='user-delete'),
]