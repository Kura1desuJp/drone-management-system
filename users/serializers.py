from rest_framework import serializers
from django.contrib.auth.models import User, Group


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False,
    )
    group_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'is_staff', 'is_active', 'groups', 'group_names', 'password']

    def get_group_names(self, obj):
        return [g.name for g in obj.groups.all()]

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        user.groups.set(groups)
        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if groups is not None:
            instance.groups.set(groups)
        return instance


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']
