from django.urls import path

from stats.views import BestPostsView

urlpatterns = [
    path('<int:group_id>/best/', BestPostsView.as_view())
]
