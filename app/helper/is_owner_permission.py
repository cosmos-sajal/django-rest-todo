from rest_framework import permissions


class IsOwnerPermission(permissions.BasePermission):
	"""
	Object level permission
	"""
	def has_object_permission(self, request, view, obj):
		return request.user.id == obj.user.id