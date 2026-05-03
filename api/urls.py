from django.urls import path
from api.views import registerUser,userLogin,userLogout,deviceLiveLocation,SoSHistory

urlpatterns = [
    path('register/', registerUser, name='register'),
    path('login/', userLogin, name='login'),
    path('logout/', userLogout, name='logout'),
    path('SOS/', SoSHistory,name='sos'),
    path('livelocation/',deviceLiveLocation, name='liveLocation')
]