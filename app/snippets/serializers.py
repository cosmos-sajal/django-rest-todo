from django.contrib.auth.models import User
from rest_framework import serializers
from .models.snippet import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES


class SnippetSerializer(serializers.Serializer):
	id = serializers.IntegerField(read_only=True)
	title = serializers.CharField(required=False, allow_blank=True, max_length=100)
	code = serializers.CharField(style={'base_template': 'textarea.html'})
	linenos = serializers.BooleanField(required=False)
	language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
	style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')
	uuid = serializers.UUIDField(required=False)
	user = serializers.ReadOnlyField(source='user.name')

	def create(self, validated_data):
		"""
		Create and return a new `Snippet` instance, given the validated data.
		"""
		return Snippet.objects.create(**validated_data)


	def update(self, instance, validated_data):
		"""
		Update and return an existing `Snippet` instance, given the validated data.
		"""
		instance.title = validated_data.get('title', instance.title)
		instance.code = validated_data.get('code', instance.code)
		instance.linenos = validated_data.get('linenos', instance.linenos)
		instance.language = validated_data.get('language', instance.language)
		instance.style = validated_data.get('style', instance.style)
		instance.save()

		return instance


class UserListSerializer(serializers.ModelSerializer):
	snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.filter(is_deleted=False))

	class Meta:
		model = User
		fields = ['id', 'snippets', 'username']


class UserDetailtSerializer(serializers.ModelSerializer):
	snippets = SnippetSerializer(many=True, read_only=True)

	class Meta:
		model = User
		fields = ['id', 'snippets', 'username', 'email']
