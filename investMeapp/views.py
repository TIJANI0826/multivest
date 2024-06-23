from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .forms import SignUpForm, InvestmentForm, ROIForm, MemberForm, WithdrawalRequestForm,LoginForm
from .models import Members, Investment, MonthlyROI, WithdrawalRequest
from django.core.mail import send_mail
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from django.conf import settings
from paystackapi.transfer import Transfer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
from multivestshop.views import is_member

paystack_secret_key = 'your_paystack_secret_key'
paystack = Paystack(secret_key=paystack_secret_key)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            user.save()
            code = str(user.id)+user.username+user.email[:user.email.index('@')]
            Members.objects.create(email=user.email,first_name=user.first_name,last_name=user.last_name,code=code)
            user = authenticate(request,username=username,password=password1)
            if user is not None:
                login(request,user)
                return redirect('investmeapp:investment')
    else:
        form = SignUpForm()
    return render(request, 'investMe/signup.html', {'form': form,})

@login_required()
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
            return redirect('investmeapp:investment')
    else:
        form = InvestmentForm()

    return render(request, 'investMe/investment.html', {'form': form, 'investments': investments, 'rois': rois, 'is_member' : is_member(request)})

@login_required
def profile(request):
    member = Members.objects.get(email=request.user.email)
    return render(request, 'investMe/profile.html', {'member': member, 'is_member' : is_member(request)})

@login_required
def update_profile(request):
    member = Members.objects.get(email=request.user.email)
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            return redirect('investmeapp:profile')
    else:
        form = MemberForm(instance=member)
    return render(request, 'investMe/update_profile.html', {'form': form, 'is_member' : is_member(request)})

@login_required
def request_withdrawal(request):
    member = Members.objects.get(email=request.user.email)
    if request.method == 'POST':
        form = WithdrawalRequestForm(request.POST)
        if form.is_valid():
            withdrawal_request = form.save(commit=False)
            withdrawal_request.member = member
            withdrawal_request.save()
            send_mail(
                'New Withdrawal Request',
                f'Member {member.name()} has requested a withdrawal of {withdrawal_request.amount}.',
                'from@example.com',
                ['admin@example.com'],
            )
            return redirect('investmeapp:investment')
    else:
        form = WithdrawalRequestForm()
    return render(request, 'investMe/request_withdrawal.html', {'form': form,'is_member' : is_member(request)})

@user_passes_test(lambda u: u.is_superuser)
def manage_members(request):
    members = Members.objects.all()
    return render(request, 'investMe/manage_members.html', {'members': members})

@user_passes_test(lambda u: u.is_superuser)
def delete_member(request, member_id):
    member = Members.objects.get(id=member_id)
    member.delete()
    return redirect('investmeapp:manage_members')

@user_passes_test(lambda u: u.is_superuser)
def update_investment(request, investment_id):
    investment = Investment.objects.get(id=investment_id)
    if request.method == 'POST':
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            form.save()
            return redirect('investmeapp:manage_members')
    else:
        form = InvestmentForm(instance=investment)
    return render(request, 'investMe/update_investment.html', {'form': form})

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
            return redirect('investmeapp:manage_members')
    else:
        form = ROIForm()
    return render(request, 'investMe/update_roi.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def manage_withdrawals(request):
    withdrawals = WithdrawalRequest.objects.filter(approved=False)
    return render(request, 'investMe/manage_withdrawals.html', {'withdrawals': withdrawals})

@user_passes_test(lambda u: u.is_superuser)
def approve_withdrawal(request, withdrawal_id):
    withdrawal = get_object_or_404(WithdrawalRequest, id=withdrawal_id)
    withdrawal.approved = True
    withdrawal.save()
    # Integrate Paystack payment to send money to member's bank account
    send_money_to_bank_account(withdrawal)
    return redirect('investmeapp:manage_withdrawals')

def send_money_to_bank_account(withdrawal):
    member = withdrawal.member
    bank_account = member.bank_account
    bank_name = member.bank_name
    amount = withdrawal.amount

    BANK_CODES = {
        'GTBank': '058',
        'Access Bank': '044',
        # Add other banks...
    }

    bank_code = BANK_CODES.get(bank_name)
    if not bank_code:
        send_mail(
            'Withdrawal Failed',
            f'Bank name {bank_name} is not supported. Please contact support.',
            'from@example.com',
            [member.email],
        )
        return

    # Create recipient code
    response = paystack.transferrecipient.create(
        type="nuban",
        name=member.name(),
        account_number=bank_account,
        bank_code=bank_code,
        currency="NGN"
    )

    if response['status']:
        recipient_code = response['data']['recipient_code']

        # Initialize transfer
        transfer_response = Transfer.initiate(
            source="balance",
            reason=f"Withdrawal for {member.name()}",
            amount=int(amount * 100),
            recipient=recipient_code
        )

        if transfer_response['status']:
            # Transfer successful
            send_mail(
                'Withdrawal Processed',
                f'Your withdrawal request of {amount} has been processed successfully.',
                'from@example.com',
                [member.email],
            )
        else:
            # Handle transfer error
            send_mail(
                'Withdrawal Failed',
                f'Your withdrawal request of {amount} failed. Please contact support.',
                'from@example.com',
                [member.email],
            )
    else:
        # Handle recipient creation error
        send_mail(
            'Withdrawal Failed',
            f'Your withdrawal request of {amount} failed. Please contact support.',
            'from@example.com',
            [member.email],
        )

@csrf_exempt
def paystack_webhook(request):
    # Handle Paystack webhook notifications
    event = json.loads(request.body)
    if event['event'] == 'transfer.success':
        reference = event['data']['reference']
        # Update your database with the transfer success status
        # Example: mark the withdrawal as completed
    return JsonResponse({'status': 'success'})