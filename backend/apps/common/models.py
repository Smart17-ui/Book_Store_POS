import uuid

from django.db import models


class UUIDModel(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class AuditLog(UUIDModel):
	user = models.ForeignKey(
		'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
		related_name='audit_logs',
	)
	action = models.CharField(max_length=100)
	entity_type = models.CharField(max_length=100)
	entity_id = models.UUIDField(null=True, blank=True)
	details = models.JSONField(null=True, blank=True)
	ip_address = models.GenericIPAddressField(null=True, blank=True)

	def __str__(self):
		return f'{self.action} {self.entity_type}'
