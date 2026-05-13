from django.urls import path

from social_entities.views import PlatformsView, GroupsViewByID, CheckGroupAccessView, GroupsViewBySlug, \
    CompareGroupsView

urlpatterns = [
    path('platforms/', PlatformsView.as_view({"get": "list", "post": "create"}), name='platforms'),

    path('groups/', GroupsViewByID.as_view({"get": "list", "post": "create"}), name='groups-get-create'),
    path('groups/<int:pk>/', GroupsViewByID.as_view(
        {"delete": "destroy", "patch": "partial_update"}
    ), name='groups-delete-update'),
    path('groups/compare/', CompareGroupsView.as_view(), name='compare-groups'),
    path('groups/<str:slug>/', GroupsViewBySlug.as_view({"get": "retrieve"}), name='groups-retrieve'),
    path('group/check-access/', CheckGroupAccessView.as_view(), name='check-group-access'),
]
