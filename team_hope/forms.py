from django import forms

class RegisterForm(forms.Form):
    # Optional checkbox (email subscription)
    subscribe_updates = forms.BooleanField(required=False, label="Subscribe to emails (optional)")

    # Optional checkbox (recovery subscription)
    subscribe_recovery = forms.BooleanField(required=False, label="Subscribe to 30-day recovery program.")

    # Required checkbox (certification)
    certify = forms.BooleanField(required=True, label="I certify that all my registration information is current and correct.")