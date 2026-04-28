from django.urls import path

from stats.views import SnapshotView

urlpatterns = [
    path('snapshot/', SnapshotView.as_view(), name='snapshots')
]