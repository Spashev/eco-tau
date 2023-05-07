from rest_framework import serializers
from product.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = (
            'product',
            'parent',
            'reply',
            'content',
            'user'
        )


class CommentListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.full_name')

    class Meta:
        model = Comment
        fields = (
            'parent',
            'reply',
            'content',
            'user',
            'date_posted'
        )
