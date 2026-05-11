from django.urls import path

from stats.views import BestPostsView, SnapshotView

urlpatterns = [
    path('<int:group_id>/best/', BestPostsView.as_view()),
    path('<int:group_id>/', SnapshotView.as_view({"get": "list"}))
]
