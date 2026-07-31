from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from .models import SkillExchangeRequest, Feedback
from .forms import SkillExchangeRequestForm, FeedbackForm
from notifications.models import create_notification

@login_required
def send_request_view(request, receiver_username):
    receiver_user = get_object_or_404(User, username=receiver_username)

    if receiver_user == request.user:
        messages.error(request, "You cannot send a skill exchange request to yourself.")
        return redirect('dashboard')

    # Check for existing active requests
    existing_request = SkillExchangeRequest.objects.filter(
        (Q(sender=request.user, receiver=receiver_user) | Q(sender=receiver_user, receiver=request.user)),
        status__in=['Pending', 'Accepted']
    ).first()

    if existing_request:
        messages.warning(request, f"You already have an active or pending request (#{existing_request.id}) with {receiver_user.first_name or receiver_user.username}.")
        return redirect('requests_list')

    if request.method == 'POST':
        form = SkillExchangeRequestForm(request.POST, sender_user=request.user, receiver_user=receiver_user)
        if form.is_valid():
            req_obj = form.save(commit=False)
            req_obj.sender = request.user
            req_obj.receiver = receiver_user
            req_obj.status = 'Pending'
            req_obj.save()

            # Trigger notification to receiver
            create_notification(
                recipient=receiver_user,
                actor=request.user,
                verb=f"sent you a new exchange request to learn {req_obj.skill_requested.name}.",
                target_url=reverse('requests_list') + '?tab=received'
            )

            messages.success(request, f"Skill exchange request sent to {receiver_user.first_name or receiver_user.username} successfully!")
            return redirect('requests_list')
        else:
            messages.error(request, "Failed to send request. Please review the choices below.")
    else:
        form = SkillExchangeRequestForm(sender_user=request.user, receiver_user=receiver_user)

    context = {
        'receiver_user': receiver_user,
        'form': form,
    }
    return render(request, 'exchanges/send_request.html', context)


@login_required
def requests_list_view(request):
    tab = request.GET.get('tab', 'received')

    received_pending = SkillExchangeRequest.objects.filter(receiver=request.user, status='Pending')
    sent_pending = SkillExchangeRequest.objects.filter(sender=request.user, status='Pending')
    active_exchanges = SkillExchangeRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status='Accepted'
    )
    completed_exchanges = SkillExchangeRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status__in=['Completed', 'Rejected', 'Cancelled']
    )

    context = {
        'tab': tab,
        'received_pending': received_pending,
        'sent_pending': sent_pending,
        'active_exchanges': active_exchanges,
        'completed_exchanges': completed_exchanges,
    }
    return render(request, 'exchanges/requests_list.html', context)


@login_required
def respond_request_view(request, request_id, action):
    req_obj = get_object_or_404(SkillExchangeRequest, id=request_id)

    if action == 'accept':
        if req_obj.receiver != request.user:
            messages.error(request, "You are not authorized to accept this request.")
            return redirect('requests_list')
        if req_obj.status != 'Pending':
            messages.warning(request, "This request is no longer pending.")
            return redirect('requests_list')
        req_obj.status = 'Accepted'
        req_obj.save()

        # Trigger notification
        create_notification(
            recipient=req_obj.sender,
            actor=request.user,
            verb="accepted your skill exchange request!",
            target_url=reverse('requests_list') + '?tab=active'
        )

        messages.success(request, f"Accepted exchange request with {req_obj.sender.username}!")

    elif action == 'reject':
        if req_obj.receiver != request.user:
            messages.error(request, "You are not authorized to reject this request.")
            return redirect('requests_list')
        if req_obj.status != 'Pending':
            messages.warning(request, "This request is no longer pending.")
            return redirect('requests_list')
        req_obj.status = 'Rejected'
        req_obj.save()

        # Trigger notification
        create_notification(
            recipient=req_obj.sender,
            actor=request.user,
            verb="declined your skill exchange request.",
            target_url=reverse('requests_list') + '?tab=sent'
        )

        messages.info(request, f"Rejected exchange request from {req_obj.sender.username}.")

    elif action == 'cancel':
        if req_obj.sender != request.user:
            messages.error(request, "You are not authorized to cancel this request.")
            return redirect('requests_list')
        if req_obj.status != 'Pending':
            messages.warning(request, "You can only cancel pending requests.")
            return redirect('requests_list')
        req_obj.status = 'Cancelled'
        req_obj.save()
        messages.info(request, "Exchange request cancelled.")

    elif action == 'complete':
        if request.user not in [req_obj.sender, req_obj.receiver]:
            messages.error(request, "You are not a participant in this exchange.")
            return redirect('requests_list')
        if req_obj.status != 'Accepted':
            messages.warning(request, "Only active exchanges can be marked as completed.")
            return redirect('requests_list')
        req_obj.status = 'Completed'
        req_obj.save()

        # Trigger notification
        other_participant = req_obj.receiver if req_obj.sender == request.user else req_obj.sender
        create_notification(
            recipient=other_participant,
            actor=request.user,
            verb="marked your skill exchange as completed.",
            target_url=reverse('requests_list') + '?tab=completed'
        )

        messages.success(request, "Skill exchange marked as Completed! Please leave feedback for your learning partner.")
        return redirect('add_feedback', request_id=req_obj.id)

    return redirect('requests_list')


@login_required
def add_feedback_view(request, request_id):
    exchange_req = get_object_or_404(SkillExchangeRequest, id=request_id)

    if exchange_req.status != 'Completed':
        messages.error(request, "Feedback can only be submitted for completed exchanges.")
        return redirect('requests_list')

    if request.user not in [exchange_req.sender, exchange_req.receiver]:
        messages.error(request, "You were not a participant in this skill exchange.")
        return redirect('requests_list')

    # Check for existing feedback by this user
    if Feedback.objects.filter(exchange_request=exchange_req, reviewer=request.user).exists():
        messages.info(request, "You have already submitted feedback for this exchange.")
        return redirect('requests_list')

    partner = exchange_req.receiver if exchange_req.sender == request.user else exchange_req.sender

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.exchange_request = exchange_req
            feedback.reviewer = request.user
            feedback.save()

            # Trigger notification
            create_notification(
                recipient=partner,
                actor=request.user,
                verb=f"left a {feedback.rating}-star review for your exchange.",
                target_url=reverse('profile_detail', kwargs={'username': partner.username})
            )

            messages.success(request, f"Thank you! Your feedback for {partner.first_name or partner.username} has been saved.")
            return redirect('requests_list')
        else:
            messages.error(request, "Error saving feedback. Please check your inputs.")
    else:
        form = FeedbackForm()

    context = {
        'exchange_req': exchange_req,
        'partner': partner,
        'form': form,
    }
    return render(request, 'exchanges/feedback.html', context)
