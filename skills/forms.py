from django import forms
from .models import Skill, UserSkill

class UserSkillAddForm(forms.Form):
    EXISTING_OR_NEW_CHOICES = [
        ('existing', 'Choose from existing skills'),
        ('new', 'Add a new custom skill'),
    ]

    add_type = forms.ChoiceField(
        choices=EXISTING_OR_NEW_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='existing'
    )
    
    # Existing skill field
    existing_skill = forms.ModelChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Skill"
    )

    # New skill fields
    new_skill_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. React.js, Python, Digital Photography'}),
        label="New Skill Name"
    )
    new_skill_category = forms.ChoiceField(
        choices=Skill.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Category"
    )
    new_skill_description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Brief description of the skill...'}),
        required=False,
        label="Description (Optional)"
    )

    # Skill details for user
    skill_type = forms.ChoiceField(
        choices=UserSkill.SKILL_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Skill Type"
    )
    proficiency_level = forms.ChoiceField(
        choices=UserSkill.PROFICIENCY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='Intermediate',
        label="Proficiency Level"
    )

    def clean(self):
        cleaned_data = super().clean()
        add_type = cleaned_data.get('add_type')
        existing_skill = cleaned_data.get('existing_skill')
        new_name = cleaned_data.get('new_skill_name')

        if add_type == 'existing':
            if not existing_skill:
                self.add_error('existing_skill', "Please select a skill from the list.")
        elif add_type == 'new':
            if not new_name or not new_name.strip():
                self.add_error('new_skill_name', "Please enter a name for the new skill.")
            else:
                # Check if skill already exists with same name case-insensitively
                existing = Skill.objects.filter(name__iexact=new_name.strip()).first()
                if existing:
                    cleaned_data['existing_skill'] = existing
                    cleaned_data['add_type'] = 'existing'

        return cleaned_data
