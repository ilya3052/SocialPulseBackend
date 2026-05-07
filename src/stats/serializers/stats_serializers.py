from rest_framework import serializers

from stats.models import Snapshot, SnapshotStats, AbsoluteStats


class SnapshotSerializer(serializers.ModelSerializer):
    from social_entities.models import Group

    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source='group',
        write_only=True
    )

    # group = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Snapshot
        fields = ('id', 'timestamp', 'type', 'group_id')


class SnapshotStatsSerializer(serializers.ModelSerializer):
    snapshot_id = serializers.PrimaryKeyRelatedField(
        queryset=Snapshot.objects.all(),
        source='snapshot',
        write_only=True
    )

    snapshot = SnapshotSerializer(read_only=True)

    class Meta:
        model = SnapshotStats
        fields = ('id', 'likes_count', 'views_count', 'participants_count', 'repost_count', 'comms_count', 'coverage',
                  'last_updated_at', 'snapshot_id', 'snapshot')

class AbsoluteStatsSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        exclude_fields = self.context.get('exclude_fields', [])

        for field in exclude_fields:
            fields.pop(field, None)
        return fields

    def get_group(self, obj):
        from social_entities.serializers import GroupSerializer
        if not obj.group:
            return None
        serializer = GroupSerializer(obj.group, context=self.context)
        return serializer.data

    class Meta:
        model = AbsoluteStats
        fields = ('id', 'likes_count', 'views_count', 'participants_count', 'repost_count', 'comms_count',
                  'posts_count', 'last_updated_at')


class BestPostsSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        exclude_fields = self.context.get('exclude_fields', [])
        for field in exclude_fields:
            fields.pop(field, None)
        return fields

    class Meta:
        model = BestPosts
        fields = ('most_liked', 'most_reposted', 'most_commented', 'most_viewed', 'last_updated_at')
