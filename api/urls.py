from django.urls import path
from api.views import registerUser,userLogin,userLogout

urlpatterns = [
    path('register/', registerUser, name='register'),
    path('login/', userLogin, name='login'),
    path('logout/', userLogout, name='logout'),
]