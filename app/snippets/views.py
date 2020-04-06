from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Snippet
from .serializers import SnippetSerializer, UserListSerializer, UserDetailtSerializer
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import renderers
from helper.is_owner_permission import IsOwnerPermission
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from rest_framework.throttling import UserRateThrottle


class UserListView(APIView):
	"""
	List all the users in the system
	"""
	def get(self, request, format=None):
		offset = int(request.GET['offset']) if request.GET.get('offset') is not None else 0
		limit = int(request.GET['limit']) if request.GET.get('limit') is not None else 10
		users = User.objects.all()[offset:offset+limit]
		count = User.objects.all().count()
		serializer = UserListSerializer(users, many=True)

		return Response({
			"data": serializer.data,
			"count": count
		})


class UserDetailView(APIView):
	"""
	List details of a single User
	"""
	def get_object(self, id):
		try:
			return User.objects.get(id=id)
		except User.DoesNotExist:
			raise Http404

	def get(self, request, id, format=None):
		user = self.get_object(id)
		serializer = UserDetailtSerializer(user)

		return Response(serializer.data)


class SnippetBaseClass(APIView):
	"""
	Base Class for Snippet actions
	"""
	permission_classes = [IsOwnerPermission]

	def get_object(self, id):
		try:
			obj = Snippet.objects.get(id=id, is_deleted=False)
			self.check_object_permissions(self.request, obj)
			return obj
		except Snippet.DoesNotExist:
			raise Http404


class SnippetHighlight(SnippetBaseClass):
	queryset = Snippet.objects.filter(is_deleted=False)
	renderer_classes = [renderers.StaticHTMLRenderer]

	def get(self, request, id, format=None):
		snippet = self.get_object(id)
		return Response(snippet.highlighted)


class SnippetListView(APIView):
	permission_classes = [permissions.IsAuthenticated]
	throttle_classes = [UserRateThrottle]

	"""
	List all code snippets , or create a new Snippet.
	"""
	def get(self, request, format=None):
		offset = int(request.GET['offset']) if request.GET.get('offset') is not None else 0
		limit = int(request.GET['limit']) if request.GET.get('limit') is not None else 10
		snippets = Snippet.objects.filter(is_deleted=False, user=request.user)[offset:offset+limit]
		count = Snippet.objects.filter(is_deleted=False, user=request.user).count()
		serializer = SnippetSerializer(snippets, many=True)

		return Response({
			"data": serializer.data,
			"count": count
		})
	
	def post(self, request, format=None):
		serializer = SnippetSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save(user=request.user)

			return Response(serializer.data, status=status.HTTP_201_CREATED)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SnippetDetailView(SnippetBaseClass):
	def get(self, request, id, format=None):
		snippet = self.get_object(id)
		serializer = SnippetSerializer(snippet)

		return Response(serializer.data)

	def put(self, request, id, format=None):
		snippet = self.get_object(id)
		serializer = SnippetSerializer(snippet, data=request.data)
		if serializer.is_valid():
			serializer.save()

			return Response(serializer.data)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, id, format=None):
		snippet = self.get_object(id)
		snippet.soft_delete()

		return Response(status=status.HTTP_204_NO_CONTENT)
