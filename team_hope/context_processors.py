from django.conf import settings # import the settings file

def azure_b2c_logout_url(request):
    # return the value you want as a dictionary. you may add multiple values in there.
    return {'AZURE_B2C_LOGOUT_URL': settings.AZURE_B2C_LOGOUT_URL}