from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *


#api for sending interest mesages to users
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_interest(request):
    try:
        serializer = SendInterestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': status.HTTP_200_OK,
                'success': True,
                'message': "Interest message sent successfully",
                'data': {}
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'message': "Validation failed",
                'errors': serializer.errors,
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'success': False,
            'message': f"Some error occurred: {str(e)}",
            'data': {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
#api for accepting or rejecting interests
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def accept_or_reject_interest(request, interest_id):
    try:
        interest = Interests.objects.get(id=interest_id, receiver=request.user)
    except Interests.DoesNotExist:
        return Response({
            'status': status.HTTP_404_NOT_FOUND,
            'success': False,
            'message': "Interest not found"
        }, status=status.HTTP_404_NOT_FOUND)
    serializer = UpdateInterestSerializer(interest, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()  
        return Response({
            'status': status.HTTP_200_OK,
            'success': True,
            'message': "Interest status updated successfully",
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    return Response({
        'status': status.HTTP_400_BAD_REQUEST,
        'success': False,
        'message': "Invalid data",
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
            

            