from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Members, Investment, MonthlyROI, WithdrawalRequest

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name','password1', 'password2')

class LoginForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password')

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['amount', 'description']

class ROIForm(forms.ModelForm):
    class Meta:
        model = MonthlyROI
        fields = ['month', 'roi']


class MemberForm(forms.ModelForm):
    class Meta:
        model = Members
        fields = '__all__'
        exclude = ['delete_flag', 'status', 'date_added' ]

class WithdrawalRequestForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['amount']

class PaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
