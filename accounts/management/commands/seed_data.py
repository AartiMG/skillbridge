from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from skills.models import Skill, UserSkill
from exchanges.models import SkillExchangeRequest, Feedback

class Command(BaseCommand):
    help = 'Seeds database with initial skills, demo student accounts, exchange requests, and feedback'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting database seeding..."))

        # 1. Create Superuser admin if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@skillbridge.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123456')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user (admin / admin123456)"))

        # 2. Create Skills
        skills_data = [
            ('Python Programming', 'Programming', 'Core Python logic, data structures, and OOP concepts.'),
            ('Web Development with Django', 'Web Development', 'Building full-stack web applications with Django.'),
            ('React.js Frontend', 'Web Development', 'Modern UI component development with React and Hooks.'),
            ('UI/UX Design', 'Design', 'Figma wireframing, prototyping, and user-centric interface design.'),
            ('Data Science & Pandas', 'Data Science', 'Data analysis, visualization with Seaborn, and Pandas manipulation.'),
            ('Machine Learning Foundations', 'Artificial Intelligence', 'Scikit-learn, regression models, and neural network basics.'),
            ('Conversational Spanish', 'Languages', 'Interactive Spanish language practice for students.'),
            ('Public Speaking & Pitching', 'Communication', 'Overcoming stage fear, slide presentation, and pitching projects.'),
            ('Flutter Mobile Apps', 'Mobile Development', 'Cross-platform mobile app development with Dart and Flutter.')
        ]

        skills_dict = {}
        for name, category, desc in skills_data:
            skill, _ = Skill.objects.get_or_create(name=name, defaults={'category': category, 'description': desc})
            skills_dict[name] = skill

        self.stdout.write(self.style.SUCCESS(f"Populated {len(skills_dict)} skills."))

        # 3. Create Sample Students
        students_info = [
            {
                'username': 'alex_rivera',
                'email': 'alex@stanford.edu',
                'first_name': 'Alex',
                'last_name': 'Rivera',
                'password': 'password123',
                'college': 'Stanford University',
                'city': 'San Francisco, CA',
                'mode': 'Online',
                'bio': 'Computer Science senior passionate about Python backend architecture, Django, and cloud deployment. Eager to master UI/UX design!',
                'teach': [('Python Programming', 'Advanced'), ('Web Development with Django', 'Advanced')],
                'learn': [('UI/UX Design', 'Beginner'), ('React.js Frontend', 'Intermediate')],
            },
            {
                'username': 'sophia_chen',
                'email': 'sophia@mit.edu',
                'first_name': 'Sophia',
                'last_name': 'Chen',
                'password': 'password123',
                'college': 'MIT',
                'city': 'Boston, MA',
                'mode': 'Both',
                'bio': 'Design student & frontend developer. Love crafting pixel-perfect interfaces in Figma. Looking for backend Python buddies!',
                'teach': [('UI/UX Design', 'Advanced'), ('React.js Frontend', 'Intermediate')],
                'learn': [('Python Programming', 'Intermediate'), ('Machine Learning Foundations', 'Beginner')],
            },
            {
                'username': 'marcus_johnson',
                'email': 'marcus@berkeley.edu',
                'first_name': 'Marcus',
                'last_name': 'Johnson',
                'password': 'password123',
                'college': 'UC Berkeley',
                'city': 'Berkeley, CA',
                'mode': 'Offline',
                'bio': 'Data science major exploring machine learning models. Native Spanish speaker happy to tutor in exchange for public speaking tips.',
                'teach': [('Data Science & Pandas', 'Advanced'), ('Conversational Spanish', 'Advanced')],
                'learn': [('Public Speaking & Pitching', 'Beginner'), ('Flutter Mobile Apps', 'Intermediate')],
            },
            {
                'username': 'priya_patel',
                'email': 'priya@nyu.edu',
                'first_name': 'Priya',
                'last_name': 'Patel',
                'password': 'password123',
                'college': 'NYU',
                'city': 'New York, NY',
                'mode': 'Both',
                'bio': 'Communication & Mobile app enthusiast building cross-platform apps in Flutter. Let us connect and share knowledge!',
                'teach': [('Flutter Mobile Apps', 'Advanced'), ('Public Speaking & Pitching', 'Intermediate')],
                'learn': [('Data Science & Pandas', 'Beginner'), ('Web Development with Django', 'Beginner')],
            }
        ]

        users_dict = {}
        for s in students_info:
            user, u_created = User.objects.get_or_create(
                username=s['username'],
                defaults={
                    'email': s['email'],
                    'first_name': s['first_name'],
                    'last_name': s['last_name'],
                }
            )
            if u_created:
                user.set_password(s['password'])
                user.save()
            
            users_dict[s['username']] = user

            # Profile update
            prof = user.profile
            prof.college_or_organization = s['college']
            prof.city = s['city']
            prof.preferred_learning_mode = s['mode']
            prof.bio = s['bio']
            prof.save()

            # Add teach skills
            for s_name, prof_level in s['teach']:
                UserSkill.objects.get_or_create(
                    profile=prof,
                    skill=skills_dict[s_name],
                    skill_type='TEACH',
                    defaults={'proficiency_level': prof_level}
                )

            # Add learn skills
            for s_name, prof_level in s['learn']:
                UserSkill.objects.get_or_create(
                    profile=prof,
                    skill=skills_dict[s_name],
                    skill_type='LEARN',
                    defaults={'proficiency_level': prof_level}
                )

        self.stdout.write(self.style.SUCCESS("Created demo student profiles & user skills."))

        # 4. Create Sample Exchanges & Feedback
        alex = users_dict['alex_rivera']
        sophia = users_dict['sophia_chen']
        marcus = users_dict['marcus_johnson']
        priya = users_dict['priya_patel']

        # Completed Exchange: Alex & Sophia
        ex1, _ = SkillExchangeRequest.objects.get_or_create(
            sender=alex,
            receiver=sophia,
            skill_offered=skills_dict['Python Programming'],
            skill_requested=skills_dict['UI/UX Design'],
            defaults={
                'message': "Hey Sophia! I saw you want to learn Python. I can teach you Python & Django in return for Figma UI/UX coaching!",
                'status': 'Completed'
            }
        )

        Feedback.objects.get_or_create(
            exchange_request=ex1,
            reviewer=alex,
            defaults={'rating': 5, 'comment': "Sophia gave fantastic feedback on my website layouts and taught me core Figma wireframing!"}
        )

        Feedback.objects.get_or_create(
            exchange_request=ex1,
            reviewer=sophia,
            defaults={'rating': 5, 'comment': "Alex explained Python classes and Django views so clearly. Super helpful peer session!"}
        )

        # Active Exchange: Marcus & Priya
        SkillExchangeRequest.objects.get_or_create(
            sender=marcus,
            receiver=priya,
            skill_offered=skills_dict['Data Science & Pandas'],
            skill_requested=skills_dict['Public Speaking & Pitching'],
            defaults={
                'message': "Hi Priya! I can help with Pandas data cleaning if you can review my project presentation pitch slides.",
                'status': 'Accepted'
            }
        )

        # Pending Exchange: Priya & Alex
        SkillExchangeRequest.objects.get_or_create(
            sender=priya,
            receiver=alex,
            skill_offered=skills_dict['Flutter Mobile Apps'],
            skill_requested=skills_dict['Web Development with Django'],
            defaults={
                'message': "Hi Alex, would love to learn Django REST backend integration for my Flutter app!",
                'status': 'Pending'
            }
        )

        # Seed Notifications
        from notifications.models import Notification
        Notification.objects.get_or_create(
            recipient=alex,
            actor=sophia,
            verb="left a 5-star review for your skill exchange.",
            defaults={'target_url': '/accounts/profile/sophia_chen/'}
        )
        Notification.objects.get_or_create(
            recipient=alex,
            actor=priya,
            verb="sent you a new exchange request to learn Web Development with Django.",
            defaults={'target_url': '/exchanges/requests/?tab=received'}
        )
        Notification.objects.get_or_create(
            recipient=priya,
            actor=marcus,
            verb="accepted your skill exchange request!",
            defaults={'target_url': '/exchanges/requests/?tab=active'}
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded sample database & notifications! Demo logins: alex_rivera, sophia_chen, marcus_johnson, priya_patel (password: password123). Admin: admin / admin123456"))
