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
    from social_entities.models import Group
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source='group',
        write_only=True
    )

    group = serializers.SerializerMethodField(read_only=True)

    def get_group(self, obj):
        from social_entities.serializers import GroupSerializer
        if not obj.group:
            return None
        serializer = GroupSerializer(obj.platform, context=self.context)
        return serializer.data

    class Meta:
        model = AbsoluteStats
        fields = ('id', 'likes_count', 'views_count', 'participants_count', 'repost_count', 'comms_count', 'coverage',
                  'last_updated_at', 'group')
        # read_only_fields = ('id', 'likes_count', 'views_count', 'participants_count', 'repost_count', 'comms_count', 'coverage',
        #           'last_updated_at', 'group')