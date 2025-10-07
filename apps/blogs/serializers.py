from rest_framework import serializers
from .models import Blog

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ["id", "title", 'images', 'description', "created_at"]
        read_only_fields= ['id', "created_at"]
