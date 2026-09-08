from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import SessionToken


class SessionTokenAuthentication(BaseAuthentication):
    keyword = 'Bearer'

    def authenticate_header(self, request):
        return self.keyword

    def authenticate(self, request):
        header = request.headers.get('Authorization', '')
        if not header:
            return None
        try:
            keyword, key = header.split(' ', 1)
        except ValueError:
            raise AuthenticationFailed('Invalid authorization header.')
        if keyword.lower() != self.keyword.lower() or not key:
            raise AuthenticationFailed('Invalid authorization header.')
        token = SessionToken.objects.select_related('user', 'user__role', 'user__client', 'user__branch').filter(
            key=key,
            user__is_active=True,
        ).first()
        if not token:
            raise AuthenticationFailed('Invalid or expired session.')
        token.last_used_at = timezone.now()
        token.save(update_fields=('last_used_at', 'updated_at'))
        return token.user, token