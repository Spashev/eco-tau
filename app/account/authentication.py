from datetime import datetime

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        jwt_token = request.META.get('HTTP_AUTHORIZATION')
        if jwt_token is None:
            return None

        jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)

        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid token signature')
        except jwt.exceptions.DecodeError:
            raise AuthenticationFailed('Invalid token format')

        email = payload.get('user_identifier')
        if email is None:
            raise AuthenticationFailed('User identifier not found in JWT')

        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.is_active:
            raise AuthenticationFailed('User not active')

        current_time = datetime.now().timestamp()
        if 'exp' in payload and payload['exp'] < current_time:
            raise AuthenticationFailed('Token has expired')

        return user, payload

    def authenticate_header(self, request):
        return 'Bearer'

    @classmethod
    def create_jwt(cls, user):
        payload = {
            'user_identifier': user.email,
            'exp': int((datetime.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']).timestamp()),
            'iat': datetime.now().timestamp(),
            'email': user.email
        }

        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return jwt_token

    @classmethod
    def create_refresh_token(cls, user):
        payload = {
            'user_identifier': user.email,
            'exp': int((datetime.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']).timestamp()),
            'email': user.email
        }

        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return jwt_token

    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace('Bearer', '').replace(' ', '')
        return token
