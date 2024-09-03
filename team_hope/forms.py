from django import forms
from .models import UserProfile, UserType, OstomateType, RelationshipStatus
from django import forms


class RegisterForm(forms.ModelForm):
    certify = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label="I agree to the terms and conditions"
    )

    class Meta:
        model = UserProfile
        fields = ['subscribed_to_email_updates', 'subscribed_to_aliveandkicking']

    def clean_certify(self):
        certify = self.cleaned_data.get('certify')
        if not certify:
            raise forms.ValidationError("You must agree to the terms and conditions to proceed.")
        return certify


class RegisterTeamHopeForm(forms.ModelForm):
    certify = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label="I agree to the terms and conditions"
    )
    surgery_type = forms.ChoiceField(
        choices=OstomateType.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
    )
    class Meta:
        model = UserProfile
        exclude = [
            'user', 'email', 'first_name', 'last_name', 'registration_complete', 'team_hope_all_complete',
            'subscribed_to_aliveandkicking', 'country', 'state_province', 'team_hope_docusign_complete',
            'team_hope_training_complete', 'aliveandkicking_waiver_complete'
        ]
        widgets = {
            'surgery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'surgery_type': forms.Select(attrs={'class': 'form-control'}),
            'surgeon_name': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Male', 'Male'),
                ('Female', 'Female'),
                ('Other', 'Other'),
            ]),
            'relationship_status': forms.Select(attrs={'class': 'form-control'}, choices=RelationshipStatus.choices),
            'pri': forms.TextInput(attrs={'class': 'form-control'}),
            'hobbies': forms.Textarea(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control'}),  # Added Bio field
        }
        

    def clean_certify(self):
        certify = self.cleaned_data.get('certify')
        if not certify:
            raise forms.ValidationError("You must agree to the terms and conditions to proceed.")
        return certify

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'user_type', 'ostomy_type', 'surgery_date', 'surgery_type',
            'surgeon_name', 'hospital_name', 'age', 'gender',
            'relationship_status', 'country', 'state_province', 'primary_language', 'secondary_language', 'hobbies',
            'subscribed_to_email_updates', 'subscribed_to_aliveandkicking'
        ]
        widgets = {
            'surgery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'ostomy_type': forms.Select(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'surgery_type': forms.TextInput(attrs={'class': 'form-control'}),
            'surgeon_name': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Male', 'Male'),
                ('Female', 'Female'),
                ('Other', 'Other'),
            ]),
            'relationship_status': forms.Select(attrs={'class': 'form-control'}, choices=RelationshipStatus.choices),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'state_province': forms.TextInput(attrs={'class': 'form-control'}),
            'primary_language': forms.TextInput(attrs={'class': 'form-control'}),
            'secondary_language': forms.TextInput(attrs={'class': 'form-control'}),
            'hobbies': forms.Textarea(attrs={'class': 'form-control textarea-short'}),
            'bio': forms.Textarea(attrs={'class': 'form-control textarea-short'}),
            'subscribed_to_email_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'subscribed_to_aliveandkicking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        ostomy_type = cleaned_data.get('ostomy_type')

        if user_type == UserType.OSTOMATE and not ostomy_type:
            self.add_error('ostomy_type', 'Ostomy type is required for Ostomates.')

        if user_type == UserType.CONSIDERING_SURGERY and not ostomy_type:
            cleaned_data['ostomy_type'] = OstomateType.OTHER  # Set to Other if not provided

        return cleaned_data



class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']  # Ensure this field is correct
