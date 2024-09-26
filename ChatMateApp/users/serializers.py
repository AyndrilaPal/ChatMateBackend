from .models import *
from rest_framework import serializers
from django.core.exceptions import ValidationError
import re,imghdr

#user serializer
class UserSerailizer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','first_name','last_name','bio','mobile','gender','address','email','username','date_of_birth','profile_image','created_at','updated_at')

    def get_profile_image_url(self,obj):
        if obj.profile_image:
            return self.context['request'].build_absolute_uri(obj.profile_image.url)
        return None

#login serializer
class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)
    password=serializers.CharField(write_only=True,required=True)

#logout serializer
class LogoutSerializer(serializers.Serializer):
    pass

#Forgot password serializer
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

#Change password serializer
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect old password.")
        return value

    def validate(self, data):
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("New passwords do not match.")

        return data     

#verify otp serializer
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)     

#reset password serializer
class ResetPasswordSerializer(serializers.Serializer):
       email = serializers.EmailField(required=True)
       new_password = serializers.CharField(required=True)
       confirm_password = serializers.CharField(required=True)
       def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("The new passwords do not match.")
        return data
       
#register user serializer
class RegisterUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    mobile = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    bio = serializers.CharField(required=False, allow_blank=True)  
    date_of_birth = serializers.DateField(required=False) 
    gender = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    profile_image=serializers.ImageField(required=False)
    
    def validate_first_name(self, value):
        if not re.match(r'^[A-Za-z]*$', value):
            raise serializers.ValidationError("Invalid first name format")
        return value
    
    def validate_last_name(self, value):
        if not re.match(r'^[A-Za-z]*$', value):
            raise serializers.ValidationError("Invalid last name format")
        return value
    
    def validate_mobile(self, value):
        if not re.match(r'^(\+\d{1,3}[- ]?)?\d{10}$', value):
            raise serializers.ValidationError("Invalid mobile format")
        return value
    
    def validate_email(self, value):
        if not re.match(r'^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|[a-z0-9]+\.)+[a-z]{2,}$', value):
            raise serializers.ValidationError("Invalid email format")
        return value
    def validate_profile_image(self, value):
        image_format = imghdr.what(value)
        if not image_format:
            raise serializers.ValidationError("The uploaded file is not a valid image.")
        return value
   
    def create(self, validated_data):
        return User.objects.create(**validated_data)       

#update user serializer       
class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','mobile','gender','bio','username','date_of_birth','profile_image','address','created_at','updated_at']
    def update(self, instance, validated_data):
        print(instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.email = validated_data.get('email', instance.email)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.address=validated_data.get('address',instance.address)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        
        instance.save()
        return instance

    def validate_mobile(self, value):
        if value and len(str(value)) != 10:
            raise ValidationError("Mobile number must be exactly 10 digits.")
        return value

    def validate_email(self, value):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            validate_email(value)
        except DjangoValidationError:
            raise ValidationError("Invalid email format.")
        return value

    def validate(self, data):
        if 'first_name' in data and not data['first_name'].isalpha():
            raise ValidationError("First name must contain only alphabetic characters.")
        if 'last_name' in data and not data['last_name'].isalpha():
            raise ValidationError("Last name must contain only alphabetic characters.")
        return data
    
#profile image serializer
class ProfileImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image']       
    def update(self,instance,validated_data):
        profile_image=validated_data.get('profile_image',None)
        if profile_image:
            instance.profile_image=profile_image
        instance.save()
        return instance    