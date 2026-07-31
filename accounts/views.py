from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .models import Profile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from skills.models import Skill, UserSkill
from exchanges.models import SkillExchangeRequest, Feedback

def home_view(request):
    total_students = Profile.objects.count()
    total_skills = Skill.objects.count()
    completed_exchanges = SkillExchangeRequest.objects.filter(status='Completed').count()
    
    popular_categories = Skill.CATEGORY_CHOICES
    popular_skills = Skill.objects.annotate(learner_count=Count('user_skills')).order_by('-learner_count')[:6]

    context = {
        'total_students': total_students,
        'total_skills': total_skills,
        'completed_exchanges': completed_exchanges,
        'popular_categories': popular_categories,
        'popular_skills': popular_skills,
    }
    return render(request, 'home.html', context)

def about_view(request):
    return render(request, 'about.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Profile is auto-created via post_save signal
            login(request, user)
            messages.success(request, f"Welcome to SkillBridge, {user.first_name}! Your account has been created successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Authenticate by username or email
        user = authenticate(request, username=username_or_email, password=password)
        if user is None and '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'dashboard')
        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')

@login_required
def dashboard_view(request):
    profile = request.user.profile
    
    teach_skills_count = profile.get_skills_teach().count()
    learn_skills_count = profile.get_skills_learn().count()
    
    pending_received = SkillExchangeRequest.objects.filter(receiver=request.user, status='Pending').count()
    pending_sent = SkillExchangeRequest.objects.filter(sender=request.user, status='Pending').count()
    
    active_exchanges = SkillExchangeRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status='Accepted'
    ).order_by('-updated_at')

    recent_requests = SkillExchangeRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-created_at')[:5]

    context = {
        'profile': profile,
        'teach_skills_count': teach_skills_count,
        'learn_skills_count': learn_skills_count,
        'pending_received': pending_received,
        'pending_sent': pending_sent,
        'active_exchanges': active_exchanges,
        'recent_requests': recent_requests,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_view(request):
    profile = request.user.profile
    teach_skills = profile.get_skills_teach()
    learn_skills = profile.get_skills_learn()

    completed_exchanges_count = SkillExchangeRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status='Completed'
    ).count()

    feedbacks = Feedback.objects.filter(
        exchange_request__in=SkillExchangeRequest.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user),
            status='Completed'
        )
    ).exclude(reviewer=request.user).order_by('-created_at')

    recent_activities = request.user.notifications.all()[:5]

    context = {
        'profile': profile,
        'teach_skills': teach_skills,
        'learn_skills': learn_skills,
        'completed_exchanges_count': completed_exchanges_count,
        'feedbacks': feedbacks,
        'recent_activities': recent_activities,
        'is_own_profile': True,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_edit_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'accounts/profile_edit.html', context)

def explore_learners_view(request):
    queryset = Profile.objects.select_related('user').all()

    query = request.GET.get('q', '').strip()
    skill_filter = request.GET.get('skill', '').strip()
    category_filter = request.GET.get('category', '').strip()
    city_filter = request.GET.get('city', '').strip()
    mode_filter = request.GET.get('mode', '').strip()
    sort_by = request.GET.get('sort', 'newest').strip()

    if query:
        queryset = queryset.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(college_or_organization__icontains=query) |
            Q(bio__icontains=query)
        )

    if skill_filter:
        queryset = queryset.filter(user_skills__skill__name__icontains=skill_filter)

    if category_filter:
        queryset = queryset.filter(user_skills__skill__category=category_filter)

    if city_filter:
        queryset = queryset.filter(city__icontains=city_filter)

    if mode_filter:
        queryset = queryset.filter(preferred_learning_mode=mode_filter)

    # Distinct before sorting/annotating
    queryset = queryset.distinct()

    # Sorting
    if sort_by == 'alphabetical':
        queryset = queryset.order_by('user__first_name', 'user__username')
    elif sort_by == 'most_skills':
        queryset = queryset.annotate(skill_cnt=Count('user_skills')).order_by('-skill_cnt')
    elif sort_by == 'highest_rated':
        # Sort in python or order by created
        profiles_list = list(queryset)
        profiles_list.sort(key=lambda p: (p.average_rating() or 0), reverse=True)
        queryset = profiles_list
    else:
        # newest default
        if isinstance(queryset, list):
            queryset.sort(key=lambda p: p.created_at, reverse=True)
        else:
            queryset = queryset.order_by('-created_at')

    # Pagination
    paginator = Paginator(queryset, 6) # 6 profiles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Skill.CATEGORY_CHOICES

    context = {
        'profiles': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'skill_filter': skill_filter,
        'category_filter': category_filter,
        'city_filter': city_filter,
        'mode_filter': mode_filter,
        'sort_by': sort_by,
    }
    return render(request, 'accounts/explore.html', context)

def profile_detail_view(request, username):
    user_obj = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user_obj)
    
    # If viewing own profile detail, redirect to profile page
    if request.user.is_authenticated and request.user == user_obj:
        return redirect('profile')

    teach_skills = profile.get_skills_teach()
    learn_skills = profile.get_skills_learn()

    completed_exchanges_count = SkillExchangeRequest.objects.filter(
        Q(sender=user_obj) | Q(receiver=user_obj),
        status='Completed'
    ).count()

    feedbacks = Feedback.objects.filter(
        exchange_request__in=SkillExchangeRequest.objects.filter(
            Q(sender=user_obj) | Q(receiver=user_obj),
            status='Completed'
        )
    ).exclude(reviewer=user_obj).order_by('-created_at')

    # Check if active request already exists between logged in user and this target user
    existing_request = None
    if request.user.is_authenticated:
        existing_request = SkillExchangeRequest.objects.filter(
            (Q(sender=request.user, receiver=user_obj) | Q(sender=user_obj, receiver=request.user)),
            status__in=['Pending', 'Accepted']
        ).first()

    context = {
        'target_user': user_obj,
        'profile': profile,
        'teach_skills': teach_skills,
        'learn_skills': learn_skills,
        'completed_exchanges_count': completed_exchanges_count,
        'feedbacks': feedbacks,
        'existing_request': existing_request,
    }
    return render(request, 'accounts/profile_detail.html', context)
