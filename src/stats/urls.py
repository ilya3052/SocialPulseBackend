from django.urls import path

from stats.views import SnapshotStatsView, AbsoluteStatsView

urlpatterns = [
    path('<int:group_id>/absolute/', AbsoluteStatsView.as_view({"get": "retrieve"}), name='absolute-stats'),
    path('<int:pk>/', SnapshotStatsView.as_view({"get": "retrieve"}, name='snapshot-stats'))
]