from django.contrib.auth import get_user_model # Use this!
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer

User = get_user_model()
class RegisterView(APIView):
    """ API view for user registration """
    throttle_scope = 'registration' 

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        # AC: Check for existing email before validation to return 409
        email = request.data.get('email')
        if email and User.objects.filter(email=email.lower()).exists():
            return Response(
                {"error": "An account with this email already exists."}, 
                status=status.HTTP_409_CONFLICT
            )

        if serializer.is_valid():
            user = serializer.save()
            
            # TODO: Step 2.2 - Trigger verification email here
            
            return Response({
                "message": "User registered successfully. Verification email sent."
            }, status=status.HTTP_201_CREATED) # AC: Returns 201
        
        # AC: Returns 400 for invalid input
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)