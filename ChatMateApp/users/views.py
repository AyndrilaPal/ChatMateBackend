from django.shortcuts import render,HttpResponse
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from users.serializers import *
import traceback,random,string,re



#custom function to validate password
def validate_custom_password(password):
    if len(password)<8 or len(password)>18:
        raise serializers.ValidationError("Password must be between 8 and 18 characters")
    if not any(char.isupper() for char in password):
        raise ValidationError("Password must contain at least one uppercase letter.")

    if not any(char.islower() for char in password):
        raise ValidationError("Password must contain at least one lowercase letter.")

    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one digit.")

    if not re.search(r"[ !@#$%^&*()_+{}\[\]:;<>,.?\/~]", password):
        raise ValidationError("Password must contain at least one special character (!@#$%^&*()_+{}[]:;<>,.?/~).")

def generate_custom_password():
    upper_case_chars = string.ascii_uppercase
    lower_case_chars = string.ascii_lowercase
    digits = string.digits
    special_chars = "@$!%*#?&"
    password = []
    password.append(random.choice(upper_case_chars))
    password.append(random.choice(lower_case_chars))
    password.append(random.choice(digits))
    password.append(random.choice(special_chars))

    remaining_length = random.randint(4, 14)  # Random length between 4 and 14 (total length - 4)
    for _ in range(remaining_length):
        password.append(random.choice(upper_case_chars + lower_case_chars + digits + special_chars))
    random.shuffle(password)
    generated_password = ''.join(password)
    return generated_password  

#home route
@api_view(['GET'])
def home(request):
    return HttpResponse('<h1>WELCOME to ChatMate,Lets connect</h1>')

#login authenticated users
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    try:
        if request.method =='POST':
            serializer=LoginSerializer(data=request.data)
            if serializer.is_valid():
                email=serializer.validated_data.get('email')
                print(email)
                password=serializer.validated_data.get('password')
                print(password)
                try:
                    user_frm_db=User.objects.get(email=email)
                    user_info={
                        'id':user_frm_db.id,
                        'email':user_frm_db.email,
                        'first_name':user_frm_db.first_name,
                        'last_name':user_frm_db.last_name,
                        'username':user_frm_db.username,
                        'bio':user_frm_db.bio,
                        'mobile':user_frm_db.mobile,
                        'gender':user_frm_db.gender,
                        'address':user_frm_db.address,
                        'profile_image':request.build_absolute_uri(user_frm_db.profile_image.url) if user_frm_db.profile_image else None,
                        'date_of_birth':user_frm_db.date_of_birth,
                        'superuser':user_frm_db.is_superuser,
                        'created_at':user_frm_db.created_at,
                        'updated_at':user_frm_db.updated_at,
                    }
                    stored_password_hash = user_frm_db.password
                    passwords_match = check_password(password, stored_password_hash)
                except User.DoesNotExist:
                    return Response({
                        'status':status.HTTP_404_NOT_FOUND,
                        'success':False,
                        'message': 'User does not exist',
                        'data':{},
                    }, status=status.HTTP_404_NOT_FOUND)
                if passwords_match:
                    refresh = RefreshToken.for_user(user_frm_db)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)
                    return Response({
                        'status':status.HTTP_200_OK,
                        'success':True,
                        'message': 'Login successful',
                        'data':{
                            'user':user_info,
                            'token': access_token,
                            'refresh_token': refresh_token,
                            },
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'status':status.HTTP_401_UNAUTHORIZED,
                        'success':False,
                        'message': 'Invalid credentials provided',
                        'data':{},
                    }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                        'status':status.HTTP_400_BAD_REQUEST,
                        'success':False,
                        'message': 'Not allowed to access',
                        'data':{},
                    }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
                        'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                        'success':False,
                        'message': 'Internal Server Error',
                        'data':{str(e)},
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#logout user
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        if request.method == 'POST':
            user = request.user
            print(user)
            refresh_token = RefreshToken.for_user(user)
            refresh_token.blacklist()
            return Response({
                        'status':status.HTTP_200_OK,
                        'success':True,
                        'message': 'User logged out sucessfully',
                        'data':{},
                    }, status=status.HTTP_200_OK)
        else:
            return Response({
                        'status':status.HTTP_405_METHOD_NOT_ALLOWED,
                        'success':False,
                        'message': 'Bad request',
                        'data':{},
                    }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        return Response({
                        'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                        'success':False,
                        'message': 'Internal Server Error',
                        'data':{},
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#utilising refresh token to get new token 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def token_refresh(request):
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({
                        'status':status.HTTP_400_BAD_REQUEST,
                        'success':False,
                        'message': 'Refresh token not provided',
                        'data':{},
                    }, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        access_token = str(token.access_token)
        new_refresh_token = str(token)
        return Response({
                        'status':status.HTTP_200_OK,
                        'success':True,
                        'message': 'Login successful',
                        'data':{
                            'token': access_token,
                            'refresh_token': new_refresh_token,
                            },
                    }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
                        'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                        'success':False,
                        'message': 'Internal Server Error',
                        'data':{},
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#route for forgot password
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    try:
        if request.method == 'POST':
            serializer=ForgotPasswordSerializer(data=request.data)
            if serializer.is_valid():
                email=serializer.validated_data.get('email')
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    return Response({
                        'status':status.HTTP_401_UNAUTHORIZED,
                        'success':False,
                        'message': 'User does not exist',
                        'data':{},
                    }, status=status.HTTP_401_UNAUTHORIZED)
                reset_token_verify_email = User.generate_reset_token(email,expiration_minutes=30)
                print(reset_token_verify_email)
                context = {
                'current_user': user,
                'username': user.username,
                'email': user.email,
                'reset_password_otp': reset_token_verify_email
                }
                email_html_message = render_to_string('email/reset_password.html', context)
                email_plaintext_message = render_to_string('email/reset_password.txt', context)
                send_mail(('Password Reset'),
                    email_plaintext_message,
                    'ayndrila2001@gmail.com', 
                    [user.email],
                    html_message=email_html_message,
                )
        return Response({
            'status':status.HTTP_200_OK,
            'success':True,
            'message': 'Password reset email sent',
            'data':{},
        },status=status.HTTP_200_OK)
    except Exception as e:
        print(traceback.format_exc())
        return Response({
            'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
            'success':False,
            'message': 'Internal Server Error',
            'data':{},
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#route for change password
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    try:
        if request.method == 'POST':
            serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                user = request.user
                new_password = serializer.validated_data['new_password']
                user.set_password(new_password)
                user.save()
                return Response({
                    'status': status.HTTP_200_OK,
                    'success': True,
                    'message': 'Password changed successfully',
                    'data': {},
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'success': False,
                    'message':  serializer.errors,
                    'data': {},
                }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'success': False,
            'message': 'Internal Server Error',
            'error': str(error),
            'data': {},
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#route for verifying otp
@api_view(['POST'])  
@permission_classes([AllowAny])   
def verify_otp(request): 
    try: 
        if request.method == 'POST':
            serializer = VerifyOTPSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                otp = serializer.validated_data.get('otp')
                try:
                    user = User.objects.get(email=email)
                    expiration_time = user.otp_expiration_time
                    if user.otp == otp:
                        user.otp=None
                        return Response({
                        'status':status.HTTP_200_OK,
                        'success':True,
                        'message': 'OTP Verified successfully',
                        'data':{},
                    },status=status.HTTP_200_OK)
                    if expiration_time < timezone.now():
                        return Response({
                        'status':status.HTTP_400_BAD_REQUEST,
                        'success':False,
                        'message': 'Expired OTP',
                        'data':{},
                    },status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({
                        'status':status.HTTP_400_BAD_REQUEST,
                        'success':False,
                        'message': 'Invalid OTP',
                        'data':{},
                    },status=status.HTTP_400_BAD_REQUEST)
                except User.DoesNotExist:
                    return Response({
                        'status':status.HTTP_404_NOT_FOUND,
                        'success':False,
                        'message': 'User does not exist',
                        'data':{},
                    }, status=status.HTTP_404_NOT_FOUND)
        return Response({
                    'status':status.HTTP_400_BAD_REQUEST,
                    'success':False,
                    'message': 'Bad Request',
                    'data':{},
                },status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
                   'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                   'success':False,
                   'message': 'Internal Server Error',
                    'data':{},
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR) 



#route for reset password
@api_view(['POST'])
@permission_classes([AllowAny])   
def reset_password(request):
    try:
        if request.method =='POST':
            serializer=ResetPasswordSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                try:
                    user = User.objects.get(email=email)
                    user.set_password(serializer.validated_data.get('new_password'))
                    user.save()
                    return Response({
                        'status':status.HTTP_200_OK,
                        'success':True,
                        'message': 'Password reset successfully',
                        'data':{},
                    },status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    return Response({
                        'status':status.HTTP_404_NOT_FOUND,
                        'success':False,
                        'message': 'User does not exist',
                        'data':{},
                    }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(traceback.format_exc())
        return Response({
                   'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                   'success':False,
                   'message': 'Internal Server Error',
                    'data':{},
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR)   


#route for register user
@api_view(['POST'])
@parser_classes([MultiPartParser])
def register_user(request):
    try:
        if request.method == 'POST':
            serializer = RegisterUserSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                new_user = serializer.save()
                generated_password = generate_custom_password()
                new_user.set_password(generated_password)
                new_user.save()
                try:
                    send_mail(
                        'Your Account Credentials',
                        f'Password: {generated_password}\n\nYou can use this password to log in. Please remember to change it after logging in for the first time.',
                        os.getenv('DEFAULT_FROM_EMAIL'),  
                        [new_user.email],  
                        fail_silently=False,
                    )
                except Exception as mail_error:
                    return Response({
                        'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                        'success': False,
                        'message': 'User registered successfully, but failed to send email.',
                        'error': str(mail_error),
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return Response({
                    'status': status.HTTP_200_OK,
                    'success': True,
                    'message': 'User registered successfully. An email has been sent with your login credentials.',
                    'data': {},
                }, status=status.HTTP_200_OK)

            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'message': 'Bad Request',
                'error': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'success': False,
            'message': 'Internal Server Error',
            'error': str(error),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
#get all users        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    try:
        if request.method == 'GET':
            user=request.user
            is_superuser=user.is_superuser
            if is_superuser:
                    print("Superuser")
                    users = User.objects.all()
                    print(users)
                    serializer = UserSerailizer(users, many=True, context={'request': request})
                    return Response({
                    'status':status.HTTP_200_OK,
                    'success':True,
                        'data':serializer.data,
                    },status=status.HTTP_200_OK)
            else:
                return Response({
                    'status':status.HTTP_403_FORBIDDEN,
                    'success':False,
                    'message': '',
                            'data':{}},status=status.HTTP_403_FORBIDDEN)
        return Response({
                        'status':status.HTTP_400_BAD_REQUEST,
                        'success':False,
                        'message': 'Bad Request',
                            'data':{}},status=status.HTTP_400_BAD_REQUEST)    
    except Exception as e:
        return Response({
                  'status':status.HTTP_500_INTERNAL_SERVER_ERROR,
                  'success':False,
                  'message': 'Internal Server Error',
                    'data':{str(e)}},status=status.HTTP_500_INTERNAL_SERVER_ERROR)        


#edit profile
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    try:
        if request.method == 'PATCH':
            user = request.user
            serializer = UserSerailizer(user, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                user_from_db = User.objects.get(email=user.email)
                user_info = {
                    'id': user_from_db.id,
                    'email': user_from_db.email,
                    'first_name': user_from_db.first_name,
                    'last_name': user_from_db.last_name,
                    'mobile': user_from_db.mobile,
                    'bio':user_from_db.bio,
                    'gender': user_from_db.gender,
                    'address': user_from_db.address,
                    'username':user_from_db.username,
                    'date_of_birth':user_from_db.date_of_birth,
                    'profile_image': request.build_absolute_uri(user_from_db.profile_image.url) if user_from_db.profile_image else None,
                    'created_at': user_from_db.created_at,
                    'updated_at': user_from_db.updated_at,
                }
                return Response({
                    'status': status.HTTP_200_OK,
                    'success': True,
                    'message': 'Profile updated successfully',
                    'data': user_info
                }, status=status.HTTP_200_OK)
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'success': False,
                'message': 'Bad Request',
                'data': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({
            'status': status.HTTP_404_NOT_FOUND,
            'success': False,
            'message': 'User not found',
        }, status=status.HTTP_404_NOT_FOUND)

#delete user        
@api_view(['DELETE'])    
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    try:
        if request.method == 'DELETE':
            user = request.user
            is_superuser = user.is_superuser
            if is_superuser:
                user_to_delete = get_object_or_404(User, id=user_id)
                if not user_to_delete:
                    return Response({
                        'status': status.HTTP_404_NOT_FOUND,
                        'success': False,
                        'message': 'User does not exist',
                        'data': {},
                    }, status=status.HTTP_404_NOT_FOUND)
                user_to_delete.delete()
                return Response({
                    'status': status.HTTP_200_OK,
                    'success': True,
                    'message': 'User deleted successfully',
                    'data': {},
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': status.HTTP_403_FORBIDDEN,
                    'success': False,
                    'message': 'You do not have permission to perform this action',
                    'data': {},
                }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'success': False,
            'message': 'Internal Server Error',
            'data': str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#update user    
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def update_user(request,user_id):
    try:
        if request.method == 'PATCH':
            user = request.user
            user_to_update = get_object_or_404(User, id=user_id)
            is_superuser = user.is_superuser
            if is_superuser:
                serializer = UpdateUserSerializer(user_to_update, data=request.data, partial=True,context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    user_info = {
                        'id': user_to_update.id,
                        'email': user_to_update.email,
                        'first_name': user_to_update.first_name,
                        'last_name': user_to_update.last_name,
                        'mobile': user_to_update.mobile,
                        'bio':user_to_update.bio,
                        'gender': user_to_update.gender,
                        'address': user_to_update.address,
                        'username':user_to_update.username,
                        'date_of_birth':user_to_update.date_of_birth,
                        'profile_image': request.build_absolute_uri(user_to_update.profile_image.url) if user_to_update.profile_image else None,
                        'created_at': user_to_update.created_at,
                        'updated_at': user_to_update.updated_at,
                    }
                    return Response({
                        'status': status.HTTP_200_OK,
                        'success': True,
                        'message': 'Profile updated successfully',
                        'data': user_info,
                    }, status=status.HTTP_200_OK)
                return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'success': False,
                    'message': 'Bad Request',
                    'data': serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                   'status': status.HTTP_403_FORBIDDEN,
                   'success': False,
                   'message': 'Not allowed. Only can update superuser',
                    'data': {},
                }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'success': False,
            'message': 'Internal Server Error',
            'data': {},
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#upload profile image
@api_view(['POST'])  
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):
    print(request.FILES)
    try:
        if request.method == 'POST':
            user = request.user
            print("user===========",user)
            old_profile_picture = user.profile_image
            serializer = ProfileImageUploadSerializer(user, data=request.data, context={'request': request})
            if serializer.is_valid():
                print(serializer)
                serializer.save()
                if old_profile_picture and old_profile_picture != user.profile_image:
                    if os.path.isfile(old_profile_picture.path):
                        os.remove(old_profile_picture.path)
                return Response({
                    'status': status.HTTP_200_OK,
                    'success': True,
                    'message': 'Profile picture updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'success': False,
                    'message': 'Bad request',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(traceback.format_exc())
        return Response({
            'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'success': False,
            'message': 'Internal Server Error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       