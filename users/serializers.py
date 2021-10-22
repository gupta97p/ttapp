from rest_framework import serializers
from .models import user_reg, Verification_Otp
from random import randint
import string
from django.core.mail import send_mail



class RegisterSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)
    email = serializers.EmailField(required=True)

    class Meta:
        model = user_reg
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}, 'user_permissions': {'write_only': True}}


    def validate_email(self, data):
        obj = user_reg.objects.filter(email=data)
        if obj:
            raise serializers.ValidationError('email must be unique')
        return data

    def validate_age(self, data):
        if data < 18 or data > 80:
            raise serializers.ValidationError("age must be between 17 to 80")
        return data

    def validate_gender(self, data):
        gender = ["Male", "Female", "Others"]
        if data not in gender:
            raise serializers.ValidationError("please select gender")
        return data


    def validate(self, attrs):
        if "username" in attrs:
            if " " in attrs['username']:
                raise serializers.ValidationError("username must not contain special characters except '.','_'")
            for i in string.punctuation:
                if (i != ".") and (i != "_"):
                    if i in attrs['username']:
                        raise serializers.ValidationError("username must not contain special characters except '.','_'")
        if 'match_played' in attrs:
            if attrs['match_played'] < attrs['match_won']:
                raise serializers.ValidationError("match won cannot be more then match_played")
        return attrs

    def create(self, validated_data):
        account = super().create(validated_data)
        password = validated_data['password']
        account.set_password(password)
        return account



class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_reg
        fields = (
            'username', 'image', 'gender', 'first_name', 'last_name', 'age', 'email', 'rank', 'match_won',
            'match_played')

    def validate_email(self, data):
        obj = user_reg.objects.filter(email=data)
        if not obj:
            return data
        raise serializers.ValidationError('email must be unique')

    def validate_age(self, age):
        if age < 18 or age > 80:
            raise serializers.ValidationError("age should be greater or equal to then 18")
        return age

    def validate(self, attrs):
        if "username" in attrs:
            if " " in attrs['username']:
                raise serializers.ValidationError("username must not contain special characters except '.','_'")
            for i in string.punctuation:
                if (i != ".") and (i != "_"):
                    if i in attrs['username']:
                        raise serializers.ValidationError("username must not contain special characters except '.','_'")
        if "email" not in attrs:
            raise serializers.ValidationError("please enter email id")
        if 'age' not in attrs:
            raise serializers.ValidationError("Please enter age")
        if "gender" not in attrs:
            raise serializers.ValidationError("please enter gender")
        return attrs


class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification_Otp
        fields = '__all__'