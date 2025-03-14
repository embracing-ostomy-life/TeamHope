from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserType(models.TextChoices):
    CONSIDERING_SURGERY = "Considering Surgery", _("Considering Surgery")
    OSTOMATE = "Ostomate", _("Ostomate")
    CAREGIVER = "care", _("Caregiver")
    MEDICAL_PROFESSIONAL = "Medical Professional", _("Medical Professional")
    SUPPORTER = "Supporter", _("Supporter")
    ADMIN = "Admin", _("Admin")


class OstomateType(models.TextChoices):
    COLOSTOMY = "Colostomy", _("Colostomy/Ileostomy")
    UROSTOMY = "Urostomy", _("Urostomy")
    OTHER = "Other", _("Other")


class TeamHopeTrainingStatus(models.TextChoices):
    NOT_STARTED = "Not Started", _("Not Started")
    IN_PROGRESS = "In Progress", _("In Progress")
    COMPLETED = "Completed", _("Completed")


class TeamHopeDocusignStatus(models.TextChoices):
    NOT_STARTED = "Not Started", _("Not Started")
    IN_PROGRESS = "In Progress", _("In Progress")
    COMPLETED = "Completed", _("Completed")


class AliveAndKickingWaiverStatus(models.TextChoices):
    NOT_STARTED = "Not Started", _("Not Started")
    IN_PROGRESS = "In Progress", _("In Progress")
    COMPLETED = "Completed", _("Completed")


class TeamHopeType(models.TextChoices):  # Corrected to inherit from TextChoices
    MENTOR = "Mentor", _("Mentor")
    MENTEE = "Mentee", _("Mentee")
    MATCHER = "Matcher", _("Matcher")


class RelationshipStatus(models.TextChoices):
    SINGLE = "Single", _("Single")
    DATING = "Dating", _("Dating")
    MARRIED = "Married", _("Married")
    DIVORCED = "Divorced", _("Divorced")
    WIDOWED = "Widowed", _("Widowed")
    SEPARATED = "Separated", _("Separated")
    OTHER = "Other", _("Other")


class EthnicityChoices(models.TextChoices):
    HISPANIC_OR_LATINO = "Hispanic or Latino", _("Hispanic or Latino")
    NOT_HISPANIC_OR_LATINO = "Not Hispanic or Latino", _("Not Hispanic or Latino")
    AMERICAN_INDIAN_OR_ALASKA_NATIVE = "American Indian or Alaska Native", _(
        "American Indian or Alaska Native"
    )
    ASIAN = "Asian", _("Asian")
    BLACK_OR_AFRICAN_AMERICAN = "Black or African American", _(
        "Black or African American"
    )
    NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER = (
        "Native Hawaiian or Other Pacific Islander",
        _("Native Hawaiian or Other Pacific Islander"),
    )
    WHITE = "White", _("White")
    OTHER = "Other", _("Other")


class PrimaryLanguageChoices(models.TextChoices):
    ENGLISH = "English", _("English")
    SPANISH = "Spanish", _("Spanish")
    FRENCH = "French", _("French")
    GERMAN = "German", _("German")
    CHINESE = "Chinese", _("Chinese")
    JAPANESE = "Japanese", _("Japanese")
    HINDI = "Hindi", _("Hindi")
    ARABIC = "Arabic", _("Arabic")
    PORTUGUESE = "Portuguese", _("Portuguese")
    RUSSIAN = "Russian", _("Russian")
    OTHER = "Other", _("Other")


class SecondaryLanguageChoices(models.TextChoices):
    ENGLISH = "English", _("English")
    SPANISH = "Spanish", _("Spanish")
    FRENCH = "French", _("French")
    GERMAN = "German", _("German")
    CHINESE = "Chinese", _("Chinese")
    JAPANESE = "Japanese", _("Japanese")
    HINDI = "Hindi", _("Hindi")
    ARABIC = "Arabic", _("Arabic")
    PORTUGUESE = "Portuguese", _("Portuguese")
    RUSSIAN = "Russian", _("Russian")
    OTHER = "Other", _("Other")
    NONE = "None", _("None")


class TeamHopeMemberRoleChoices(models.TextChoices):
    PARTICIPANT = "Participant", _("I want to Connect with a Veteran Ostomate")
    VOLUNTEER = "Volunteer", _("Veteran Ostomate Volunteer")


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(
        max_length=50,
        choices=UserType.choices,
        default=UserType.SUPPORTER,
    )
    profile_picture = models.ImageField(
        upload_to="", null=True, blank=True
    )
    surgery_date = models.DateField(null=True, blank=True)
    surgery_type = models.CharField(
        max_length=50, null=True, blank=True
    )  # Ensure this is present
    surgeon_name = models.CharField(max_length=100, null=True, blank=True)
    hospital_name = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    ethnicity = models.CharField(
        max_length=100, choices=EthnicityChoices.choices, null=True, blank=True
    )
    relationship_status = models.CharField(
        max_length=20, choices=RelationshipStatus.choices, null=True, blank=True
    )
    country = models.CharField(max_length=100, null=True, blank=True)
    state_province = models.CharField(max_length=100, null=True, blank=True)
    primary_language = models.CharField(
        max_length=100,
        choices=PrimaryLanguageChoices.choices,
        default=PrimaryLanguageChoices.ENGLISH,
        null=True,
        blank=True,
    )

    secondary_language = models.CharField(
        max_length=100,
        choices=SecondaryLanguageChoices.choices,
        default=SecondaryLanguageChoices.NONE,
        null=True,
        blank=True,
    )

    hobbies = models.TextField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    subscribed_to_email_updates = models.BooleanField(default=False)
    subscribed_to_aliveandkicking = models.BooleanField(default=False)
    team_hope_docusign_complete = models.BooleanField(default=False)
    team_hope_training_complete = models.BooleanField(default=False)
    team_hope_all_complete = models.BooleanField(default=False, editable=False)
    docusign_aliveandkicking_envelope_id = models.TextField(default="", editable=False)
    docusign_teamhope_envelope_id = models.TextField(default="", editable=False)
    subscribed_to_teamhope = models.BooleanField(default=False)
    teamhope_member_role = models.CharField(
        max_length=100,
        choices=TeamHopeMemberRoleChoices.choices,
        null=True,
        blank=True,
    )
    aliveandkicking_waiver_complete = models.BooleanField(default=False)
    registration_complete = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.team_hope_all_complete = all(
            [
                self.team_hope_docusign_complete,
                self.team_hope_training_complete,
            ]
        )

        super().save(*args, **kwargs)

    @property
    def days_until_surgery(self):
        if self.surgery_date:
            return (self.surgery_date - date.today()).days
        return None

    def __str__(self):
        return f"{self.user.username}'s profile"


class UserIdentityInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Identity info for {self.user.username} {self.uuid}"
