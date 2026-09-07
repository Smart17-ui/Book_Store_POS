from django.contrib import admin
from django.contrib.auth.hashers import identify_hasher, make_password

from .models import Permission, Role, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ('username', 'full_name', 'email', 'role', 'is_active', 'last_login')
	list_filter = ('role', 'is_active')
	search_fields = ('username', 'full_name', 'email')
	filter_horizontal = ('permissions',)
	readonly_fields = ('last_login',)

	def save_model(self, request, obj, form, change):
		try:
			identify_hasher(obj.password_hash)
		except (ValueError, AttributeError):
			obj.password_hash = make_password(obj.password_hash)
		super().save_model(request, obj, form, change)


admin.site.register([Permission, Role])
