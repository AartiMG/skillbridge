from django import forms
from .models import SkillExchangeRequest, Feedback
from skills.models import Skill, UserSkill

class SkillExchangeRequestForm(forms.ModelForm):
    class Meta:
        model = SkillExchangeRequest
        fields = ['skill_offered', 'skill_requested', 'message']
        widgets = {
            'skill_offered': forms.Select(attrs={'class': 'form-select'}),
            'skill_requested': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Hi! I would love to learn this skill from you. In return, I can help you master the skill I offered. Let us schedule a session!'
            }),
        }

    def __init__(self, *args, **kwargs):
        sender_user = kwargs.pop('sender_user', None)
        receiver_user = kwargs.pop('receiver_user', None)
        super().__init__(*args, **kwargs)

        if sender_user and hasattr(sender_user, 'profile'):
            # Offered skills should come from sender's 'Can Teach' skills
            sender_teach_skills = Skill.objects.filter(
                user_skills__profile=sender_user.profile,
                user_skills__skill_type='TEACH'
            )
            self.fields['skill_offered'].queryset = sender_teach_skills
            self.fields['skill_offered'].empty_label = "-- Select a skill you can teach --"
        else:
            self.fields['skill_offered'].queryset = Skill.objects.none()

        if receiver_user and hasattr(receiver_user, 'profile'):
            # Requested skills should come from receiver's 'Can Teach' skills
            receiver_teach_skills = Skill.objects.filter(
                user_skills__profile=receiver_user.profile,
                user_skills__skill_type='TEACH'
            )
            self.fields['skill_requested'].queryset = receiver_teach_skills
            self.fields['skill_requested'].empty_label = "-- Select a skill they can teach --"
        else:
            self.fields['skill_requested'].queryset = Skill.objects.none()


class FeedbackForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, '5 - Outstanding / Exceeded expectations'),
        (4, '4 - Great / Highly beneficial'),
        (3, '3 - Good / Met expectations'),
        (2, '2 - Fair / Needs improvement'),
        (1, '1 - Poor / Unsatisfactory'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial=5
    )

    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your learning experience, what you learned, and feedback for your peer...'
            }),
        }
