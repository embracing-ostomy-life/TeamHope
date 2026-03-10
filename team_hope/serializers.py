from django.contrib.auth import get_user_model
from rest_framework import serializers

from team_hope.models import UserProfile, UserMethodOfCommunication


class UserMethodOfCommunicationSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())

    class Meta:
        model = UserMethodOfCommunication
        fields = (
            "user",
            "profile",
        )


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.CharField(source="user.email")
    communication_method = serializers.SerializerMethodField()

    def get_communication_method(self, obj):
        """Method for returning the communication method of the user"""
        resp = ""
        seperator = ";"
        comms = UserMethodOfCommunication.objects.filter(user=obj.user.id)

        if comms:
            resp += seperator.join(list(comms.values_list("communication_method", flat=True)))
        return resp

    class Meta:
        model = UserProfile
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "email",
            "user_type",
            "profile_picture",
            "surgery_date",
            "surgery_type",
            "surgeon_name",
            "hospital_name",
            "age",
            "gender",
            "ethnicity",
            "relationship_status",
            "country",
            "state_province",
            "primary_language",
            "phone",
            "secondary_language",
            "hobbies",
            "bio",
            "notes",
            "subscribed_to_email_updates",
            "subscribed_to_aliveandkicking",
            "team_hope_docusign_complete",
            "team_hope_training_complete",
            "team_hope_all_complete",
            "docusign_aliveandkicking_envelope_id",
            "docusign_teamhope_envelope_id",
            "subscribed_to_teamhope",
            "registered_th",
            "registered_ak",
            "teamhope_member_role",
            "aliveandkicking_waiver_complete",
            "signup_complete",
            "registration_complete",
            "communication_method"

        )
