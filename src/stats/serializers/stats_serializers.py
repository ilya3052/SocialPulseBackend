from rest_framework import serializers

from stats.models import Snapshot, SnapshotStats, AbsoluteStats


class SnapshotSerializer(serializers.ModelSerializer):
    from social_entities.models import Group

    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source='group',
        write_only=True
    )

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

    class Meta:
        model = AbsoluteStats
        fields = ('id', 'likes_count', 'views_count', 'participants_count', 'repost_count', 'comms_count',
                  'posts_count', 'last_updated_at')
