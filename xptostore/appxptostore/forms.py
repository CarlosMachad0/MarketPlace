from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

# General Login
class LoginForm(forms.Form):
    username    = forms.CharField(widget= forms.TextInput(attrs={"class": "form-control"}))
    password    = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

# Client Registration
class RegisterClientForm(UserCreationForm):
    username            = forms.CharField(max_length=25,widget=forms.TextInput(attrs={"class": "form-control"}))
    first_name          = forms.CharField(max_length=25,widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name           = forms.CharField(max_length=25,widget=forms.TextInput(attrs={"class": "form-control"}))
    email               = forms.EmailField(max_length=50,widget=forms.TextInput(attrs={"class": "form-control"}))
    password1           = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2           = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    birthDate           = forms.DateField(widget=forms.DateInput(attrs={"class": "form-control"}))
    isAdmin             = forms.BooleanField(required=False,disabled=True,initial=False)
    isClient            = forms.BooleanField(required=False,disabled=True,initial=False)
    isComercialTypeOne  = forms.BooleanField(required=False,disabled=True,initial=False)
    isComercialTypeTwo  = forms.BooleanField(required=False,disabled=True,initial=False)

    class Meta:
        model = Utilizadores
        fields = ( 'username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'birthDate', 'isAdmin', 'isClient', 'isComercialTypeOne', 'isComercialTypeTwo' )

# Provider Registration
class RegisterProviderForm(forms.ModelForm):
    class Meta:
        model = Fornecedores
        fields = ( 'name', 'email', 'telephone', 'adress', 'nif', 'status')

# Product creation
class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ( 'name', 'quantity', 'description', 'price', 'promo_price', 'image', 'validated', 'status' )
        
# Category creation
class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ( 'name', 'description', 'validated', 'status' )


