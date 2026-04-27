from django.urls import path

from social_entities.views import PlatformsView, GroupsView, CheckGroupAccessView

urlpatterns = [
    path('platforms/', PlatformsView.as_view({"get": "list", "post": "create"}), name='platforms'),

    path('groups/', GroupsView.as_view({"get": "list", "post": "create"}), name='groups-get-create'),
    path('groups/<int:pk>', GroupsView.as_view({"delete": "destroy", "patch": "partial_update"}), name='groups-delete-update'),
    path('group/check-access/', CheckGroupAccessView.as_view(), name='check-group-access'),
]
