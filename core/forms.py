from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.password_validation import validate_password

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Create password'}))

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password
    
class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150)

    class Meta:
        model = Profile
        fields = ['phone', 'location', 'avatar']

    def save(self, user, commit=True):
        user.first_name = self.cleaned_data['full_name']
        if commit:
            user.save()
        return super().save(commit=commit)
