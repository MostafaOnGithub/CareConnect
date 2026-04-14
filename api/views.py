from django.shortcuts import render
from rest_framework import status, viewsets,permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from Users.serializers import UserSerializer,RegestrationSerializer
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from Users.models import User
from django.contrib.auth import authenticate
from Tracking.serializers import RoutePointSerializer
from Devices.models import Device,UserDeviceLink
from Tracking.models import DeviceLocationLog
from Devices.serializers import UserDeviceLinkSerializer
from rest_framework.authentication import TokenAuthentication

@api_view(['POST'])
def registerUser(request):
    if request.method == "POST":
        serializer = RegestrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(RegestrationSerializer(user).data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def userLogin(request):     
    if request.method == 'POST':
        username = request.data.get("username")
        password = request.data.get("password")
        user = None
        if "@" in username:
            try:
                user = User.objects.get(email=username)
            except ObjectDoesNotExist:
                pass
        if not user:
            user = authenticate(username=username,password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token':token.key},status=status.HTTP_200_OK)
        return Response({'error':'Invalid credintials'},status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def userLogout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def deviceLiveLocation(request):
    link = UserDeviceLink.objects.filter(
        user = request.user,
        is_active = True
    ).select_related("device").first()

    if not link:
        return Response({"error":"There is no device connected"}, status=status.HTTP_404_NOT_FOUND)
    
    device = link.device
    
    location = DeviceLocationLog.objects.filter(
        device = device
    ).latest('timestamp')
    if not location:
        return Response({"error":"No location data available"},status=status.HTTP_404_NOT_FOUND)
    
    serializer = RoutePointSerializer(location)
    return Response(serializer.data,status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def SoSHistory(request):
    link = UserDeviceLink.objects.filter(
        user = request.user,
        is_active = True
    ).select_related("device").first()

    if not link:
        return Response({"error":"There is no device connected"}, status=status.HTTP_404_NOT_FOUND)
    
    device = link.device


class UserDeviceLinkViewSet(viewsets.ModelViewSet):
    serializer_class = UserDeviceLinkSerializer

    authentication_classes = [TokenAuthentication] 
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # A user should only see their own device links
        return UserDeviceLink.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically link the device to the logged-in user
        serializer.save(user=self.request.user)



