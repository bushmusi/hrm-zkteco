from rest_framework import serializers


class AttendanceSerializer(serializers.Serializer):
    uid = serializers.IntegerField(required=True, max_value=60000)
    user_id = serializers.IntegerField(required=True, max_value=60000)
    timestamp = serializers.DateTimeField()
    # Which is check-in = 0, check-out = 1, Break-out = 2,
    # Break-in = 3, Overtime-in = 4 and Overtime-in = 5
    punch = serializers.CharField(max_length=100)
    # currently if u are check in finger it status =0 or
    # if u checked on face status = 15 and pwd status = 3
    status = serializers.CharField(max_length=199)


class UserSerializer(serializers.Serializer):
    uid = serializers.IntegerField(required=True, max_value=60000)
    user_id = serializers.IntegerField(required=True, max_value=60000)
    name = serializers.CharField(required=True, max_length=199)
    # privilege currently 14 for Admin and 0/3 for normal user,
    privilege = serializers.CharField(max_length=199)
    password = serializers.CharField(max_length=191, allow_blank=True)
    group_id = serializers.CharField(required=False, max_length=199)
    privilege = serializers.CharField(max_length=199)


class AttendanceSerializer(serializers.Serializer):
    uid = serializers.IntegerField(required=True, max_value=60000)
    user_id = serializers.IntegerField(required=True, max_value=60000)
    timestamp = serializers.CharField(required=True, max_length=199)
    punch = serializers.CharField(required=True, max_length=199)
    status = serializers.CharField(required=True, max_length=199)
