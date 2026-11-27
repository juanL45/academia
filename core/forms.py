from django_select2.forms import Select2Widget
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name','email','password', 'document_type', 'document_number', 'phone']        