from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Skill, UserSkill
from .forms import UserSkillAddForm

@login_required
def manage_skills_view(request):
    profile = request.user.profile
    teach_skills = profile.get_skills_teach()
    learn_skills = profile.get_skills_learn()

    if request.method == 'POST':
        form = UserSkillAddForm(request.POST)
        if form.is_valid():
            add_type = form.cleaned_data['add_type']
            skill_type = form.cleaned_data['skill_type']
            proficiency_level = form.cleaned_data['proficiency_level']

            if add_type == 'existing':
                skill_obj = form.cleaned_data['existing_skill']
            else:
                name = form.cleaned_data['new_skill_name'].strip()
                category = form.cleaned_data['new_skill_category']
                desc = form.cleaned_data['new_skill_description']
                skill_obj, created = Skill.objects.get_or_create(
                    name__iexact=name,
                    defaults={'name': name, 'category': category, 'description': desc}
                )

            # Save UserSkill
            user_skill, created = UserSkill.objects.get_or_create(
                profile=profile,
                skill=skill_obj,
                skill_type=skill_type,
                defaults={'proficiency_level': proficiency_level}
            )

            if not created:
                user_skill.proficiency_level = proficiency_level
                user_skill.save()
                messages.info(request, f"Updated proficiency for {skill_obj.name}.")
            else:
                messages.success(request, f"Added {skill_obj.name} to your skills!")

            return redirect('manage_skills')
        else:
            messages.error(request, "Error adding skill. Please check the inputs.")
    else:
        form = UserSkillAddForm()

    context = {
        'profile': profile,
        'teach_skills': teach_skills,
        'learn_skills': learn_skills,
        'form': form,
    }
    return render(request, 'skills/manage_skills.html', context)

@login_required
def remove_user_skill_view(request, skill_id):
    profile = request.user.profile
    user_skill = get_object_or_404(UserSkill, id=skill_id, profile=profile)
    skill_name = user_skill.skill.name
    user_skill.delete()
    messages.success(request, f"Removed {skill_name} from your profile.")
    return redirect('manage_skills')
