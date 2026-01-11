from django.urls import path
from api.views import registerUser,userLogin,userLogout,deviceLiveLocation

urlpatterns = [
    path('register/', registerUser, name='register'),
    path('login/', userLogin, name='login'),
    path('logout/', userLogout, name='logout'),
    path('livelocation/',deviceLiveLocation, name='liveLocation')
]