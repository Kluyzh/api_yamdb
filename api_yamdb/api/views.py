from rest_framework import viewsets
from .serializers import ReviewSerializer, CommentSerializer
from reviews.models import Review, Comment
from rest_framework.permissions import IsAdminUser


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    # permission_classes = ()

    def get_queryset(self):
        return Review.objects.filter(title=self.kwargs['title_id'])

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.kwargs['title_id']
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    # permission_classes = ()

    def get_queryset(self):
        return Comment.objects.filter(review=self.kwargs['review_id'])

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.kwargs['review_id']
        )
