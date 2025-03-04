from django import forms
from .models import Websites

class WebsiteForm(forms.ModelForm):
    class Meta:
        model = Websites
        fields = ['url']