from django import forms
from .models import (
    UserProfile,
    UserType,
    OstomateType,
    RelationshipStatus,
    TeamHopeMemberRoleChoices,
    PrimaryLanguageChoices,
    EthnicityChoices,
)
from django import forms
from django.utils.safestring import mark_safe
import datetime


class RegisterForm(forms.ModelForm):
    certify = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label=mark_safe(
            "I agree to the <a href='https://embracingostomylife.org/terms-of-use/' target='_blank'>terms and conditions</a>"
        ),
    )

    class Meta:
        model = UserProfile
        fields = ["subscribed_to_email_updates", "subscribed_to_aliveandkicking"]

    def clean_certify(self):
        certify = self.cleaned_data.get("certify")
        if not certify:
            raise forms.ValidationError(
                "You must agree to the terms and conditions to proceed."
            )
        return certify


class RegisterTeamHopeForm(forms.ModelForm):
    certify = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label="I agree to the terms and conditions",
    )

    uoaa_taken = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label=mark_safe(
            "I have completed (or plan to complete within 14 days) the UOAA online Ostomy Friends Program – <a href='https://embracingostomylife.org/courses/the-ostomy-friends-program/' target='_blank'>Click here to take the course.</a>"
        ),
    )

    surgery_type = forms.ChoiceField(
        choices=OstomateType.choices,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
    )

    surgery_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        initial=datetime.date.today,  # Set initial value to today's date
    )

    teamhope_member_role = forms.ChoiceField(
        choices=TeamHopeMemberRoleChoices.choices,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
        label="Please select your Team Hope member role",
    )

    hobbies = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}),
        required=True,
    )

    bio = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}),
        required=True,
        label="Anything else you'd like us to know?",
    )

    age = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        required=True,
    )
    gender = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "form-control"}),
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
        ],
        required=True,
    )
    relationship_status = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "form-control"}),
        choices=RelationshipStatus.choices,
        required=True,
    )

    primary_language = forms.ChoiceField(
        choices=PrimaryLanguageChoices.choices,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
        label="Primary Language",
    )

    class Meta:
        model = UserProfile
        exclude = [
            "user",
            "user_type",
            "email",
            "first_name",
            "last_name",
            "registration_complete",
            "team_hope_all_complete",
            "subscribed_to_aliveandkicking",
            "country",
            "state_province",
            "team_hope_docusign_complete",
            "team_hope_training_complete",
            "aliveandkicking_waiver_complete",
            "secondary_language",
        ]
        widgets = {
            "surgery_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "teamhope_member_role": forms.Select(attrs={"class": "form-control"}),
            "surgery_type": forms.Select(attrs={"class": "form-control"}),
            "surgeon_name": forms.TextInput(attrs={"class": "form-control"}),
            "hospital_name": forms.TextInput(attrs={"class": "form-control"}),
            "age": forms.NumberInput(attrs={"class": "form-control"}),
            "gender": forms.Select(
                attrs={"class": "form-control"},
                choices=[
                    ("Male", "Male"),
                    ("Female", "Female"),
                    ("Other", "Other"),
                ],
            ),
            "relationship_status": forms.Select(
                attrs={"class": "form-control"}, choices=RelationshipStatus.choices
            ),
            "pri": forms.TextInput(attrs={"class": "form-control"}),
            "hobbies": forms.Textarea(attrs={"class": "form-control"}),
            "bio": forms.Textarea(
                attrs={"class": "form-control"},
            ),  # Added Bio field
        }

        labels = {
            "surgeon_name": "Surgeon name(Optional)",
            "hospital_name": "Hospital name(Optional)",
        }

    def clean_surgery_date(self):
        surgery_date = self.cleaned_data.get("surgery_date")
        if not surgery_date:
            raise forms.ValidationError("The surgery date is required.")
        return surgery_date

    def clean_certify(self):
        certify = self.cleaned_data.get("certify")
        if not certify:
            raise forms.ValidationError(
                "You must agree to the terms and conditions to proceed."
            )
        return certify


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "user_type",
            "ostomy_type",
            "surgery_date",
            "surgery_type",
            "surgeon_name",
            "hospital_name",
            "age",
            "gender",
            "relationship_status",
            "country",
            "state_province",
            "primary_language",
            "secondary_language",
            "hobbies",
            "subscribed_to_email_updates",
            "subscribed_to_aliveandkicking",
        ]
        widgets = {
            "surgery_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "ostomy_type": forms.Select(attrs={"class": "form-control"}),
            "user_type": forms.Select(attrs={"class": "form-control"}),
            "surgery_type": forms.TextInput(attrs={"class": "form-control"}),
            "surgeon_name": forms.TextInput(attrs={"class": "form-control"}),
            "hospital_name": forms.TextInput(attrs={"class": "form-control"}),
            "age": forms.NumberInput(attrs={"class": "form-control"}),
            "gender": forms.Select(
                attrs={"class": "form-control"},
                choices=[
                    ("Male", "Male"),
                    ("Female", "Female"),
                    ("Other", "Other"),
                ],
            ),
            "relationship_status": forms.Select(
                attrs={"class": "form-control"}, choices=RelationshipStatus.choices
            ),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "state_province": forms.TextInput(attrs={"class": "form-control"}),
            "primary_language": forms.TextInput(attrs={"class": "form-control"}),
            "secondary_language": forms.TextInput(attrs={"class": "form-control"}),
            "hobbies": forms.Textarea(attrs={"class": "form-control textarea-short"}),
            "bio": forms.Textarea(attrs={"class": "form-control textarea-short"}),
            "subscribed_to_email_updates": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "subscribed_to_aliveandkicking": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")
        ostomy_type = cleaned_data.get("ostomy_type")

        if user_type == UserType.OSTOMATE and not ostomy_type:
            self.add_error("ostomy_type", "Ostomy type is required for Ostomates.")

        if user_type == UserType.CONSIDERING_SURGERY and not ostomy_type:
            cleaned_data["ostomy_type"] = (
                OstomateType.OTHER
            )  # Set to Other if not provided

        return cleaned_data


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["profile_picture"]  # Ensure this field is correct


class RegisterAliveAndKickingForm(forms.ModelForm):
    certify = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label=mark_safe(
            "I agree to the <a href='https://embracingostomylife.org/terms-of-use/' target='_blank'>terms and conditions</a>"
        ),
    )

    surgery_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        initial=datetime.date.today,  # Set initial value to today's date
    )

    surgery_type = forms.ChoiceField(
        choices=OstomateType.choices,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = ["surgery_date", "certify", "surgery_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only set the initial value if surgery_date is not already set
        if not self.instance.surgery_date:
            self.fields["surgery_date"].initial = datetime.date.today()

    def clean_surgery_date(self):
        surgery_date = self.cleaned_data.get("surgery_date")
        if not surgery_date:
            raise forms.ValidationError("The surgery date is required.")
        return surgery_date

    def clean_certify(self):
        certify = self.cleaned_data.get("certify")
        if not certify:
            raise forms.ValidationError(
                "You must agree to the terms and conditions to proceed."
            )
        return certify
