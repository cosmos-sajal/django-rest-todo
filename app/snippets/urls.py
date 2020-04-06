from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import SnippetListView, SnippetDetailView, UserListView, UserDetailView, SnippetHighlight

urlpatterns = [
	path('snippets/', SnippetListView.as_view()),
	path('snippets/<int:id>/', SnippetDetailView.as_view()),
	path('snippets/<int:id>/highlight', SnippetHighlight.as_view()),
	path('users/', UserListView.as_view()),
	path('users/<int:id>/', UserDetailView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
