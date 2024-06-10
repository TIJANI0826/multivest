from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import SignUpForm, InvestmentForm, ROIForm
from .models import Members, Investment, MonthlyROI
from django.utils import timezone
from datetime import datetime, timedelta

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            code = str(user.id)+user.username+user.email[:user.email.index('@')]
            Members.objects.create(email=user.email,first_name=user.first_name,last_name=user.last_name,code=code)
            user.save()
            login(request,user)
            return redirect('investment')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def investment(request):
    member = Members.objects.get(email=request.user.email)
    investments = Investment.objects.filter(member=member)
    rois = MonthlyROI.objects.filter(investment__in=investments)

    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.member = member
            investment.initial_amount = investment.amount
            investment.save()
            return redirect('investment')
    else:
        form = InvestmentForm()

    return render(request, 'investment.html', {'form': form, 'investments': investments, 'rois': rois})

@user_passes_test(lambda u: u.is_superuser)
def manage_members(request):
    members = Members.objects.all()
    return render(request, 'manage_members.html', {'members': members})

@user_passes_test(lambda u: u.is_superuser)
def delete_member(request, member_id):
    member = Members.objects.get(id=member_id)
    user = User.objects.get(email=member.email)
    member.delete()
    user.delete()
    return redirect('manage_members')

@user_passes_test(lambda u: u.is_superuser)
def update_investment(request, investment_id):
    member = Members.objects.get(id=investment_id)
    investment = Investment.objects.get(member=member)
    if request.method == 'POST':
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            form.save()
            return redirect('manage_members')
    else:
        form = InvestmentForm(instance=investment)
    return render(request, 'update_investment.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def update_roi(request):
    if request.method == 'POST':
        form = ROIForm(request.POST)
        if form.is_valid():
            roi = form.save(commit=False)
            investments = Investment.objects.all()
            for investment in investments:
                MonthlyROI.objects.update_or_create(
                    investment=investment,
                    month=roi.month,
                    defaults={'roi': roi.roi}
                )
            return redirect('manage_members')
    else:
        form = ROIForm()
    return render(request, 'update_roi.html', {'form': form})
