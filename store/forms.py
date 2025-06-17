# store/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        help_text='Required. Please enter a valid email address.'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email') # The fields that will be saved

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        # Add placeholders and classes to the fields
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'e.g., johndoe'}
        )
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'e.g., you@example.com'}
        )
        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Enter a strong password'}
        )
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Confirm your password'}
        )
        
        # Change the default labels
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Password confirmation"