#!/usr/bin/env python
"""
Script to create test data for the Mensa Member Connect application.
Run this script after starting the Django server.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/billielee/Sites/mensa-name/mensa_member_connect_backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mensa_member_connect_backend.settings')
django.setup()

from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.models.local_group import LocalGroup
from mensa_member_connect.models.industry import Industry
from mensa_member_connect.models.expert import Expert
from mensa_member_connect.models.expertise import Expertise

def create_test_data():
    print("Creating test data for Mensa Member Connect...")
    
    # Create Local Groups
    print("Creating local groups...")
    local_groups_data = [
        {"group_name": "New York City", "city": "New York", "state": "NY"},
        {"group_name": "Los Angeles", "city": "Los Angeles", "state": "CA"},
        {"group_name": "Chicago", "city": "Chicago", "state": "IL"},
        {"group_name": "Boston", "city": "Boston", "state": "MA"},
        {"group_name": "Seattle", "city": "Seattle", "state": "WA"},
    ]
    
    local_groups = []
    for group_data in local_groups_data:
        group, created = LocalGroup.objects.get_or_create(
            group_name=group_data["group_name"],
            defaults=group_data
        )
        local_groups.append(group)
        if created:
            print(f"  Created local group: {group.group_name}")
        else:
            print(f"  Local group already exists: {group.group_name}")
    
    # Create Industries
    print("Creating industries...")
    industries_data = [
        {"industry_name": "Technology", "industry_description": "Software, hardware, and digital services"},
        {"industry_name": "Healthcare", "industry_description": "Medical, pharmaceutical, and health services"},
        {"industry_name": "Finance", "industry_description": "Banking, investment, and financial services"},
        {"industry_name": "Education", "industry_description": "Teaching, research, and educational services"},
        {"industry_name": "Engineering", "industry_description": "Civil, mechanical, electrical, and other engineering fields"},
    ]
    
    industries = []
    for industry_data in industries_data:
        industry, created = Industry.objects.get_or_create(
            industry_name=industry_data["industry_name"],
            defaults=industry_data
        )
        industries.append(industry)
        if created:
            print(f"  Created industry: {industry.industry_name}")
        else:
            print(f"  Industry already exists: {industry.industry_name}")
    
    # Create Test Users
    print("Creating test users...")
    
    # Regular test user
    test_user, created = CustomUser.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'member_id': 123456,
            'city': 'New York',
            'state': 'NY',
            'role': 'member',
            'status': 'active',
            'local_group': local_groups[0],  # NYC group
        }
    )
    if created:
        test_user.set_password('TestPassword123!')
        test_user.save()
        print(f"  Created test user: {test_user.username}")
    else:
        print(f"  Test user already exists: {test_user.username}")
    
    # Admin test user
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'member_id': 999999,
            'city': 'Los Angeles',
            'state': 'CA',
            'role': 'admin',
            'status': 'active',
            'is_staff': True,  # Required for admin permissions
            'local_group': local_groups[1],  # LA group
        }
    )
    if created:
        admin_user.set_password('AdminPassword123!')
        admin_user.save()
        print(f"  Created admin user: {admin_user.username}")
    else:
        # Update existing admin user to have is_staff=True
        if not admin_user.is_staff:
            admin_user.is_staff = True
            admin_user.save()
            print(f"  Admin user already exists and updated with is_staff=True: {admin_user.username}")
        else:
            print(f"  Admin user already exists: {admin_user.username}")
    
    # Expert test user
    expert_user, created = CustomUser.objects.get_or_create(
        username='expert',
        defaults={
            'email': 'expert@example.com',
            'first_name': 'Expert',
            'last_name': 'Member',
            'member_id': 789012,
            'city': 'Chicago',
            'state': 'IL',
            'role': 'member',
            'status': 'active',
            'local_group': local_groups[2],  # Chicago group
        }
    )
    if created:
        expert_user.set_password('ExpertPassword123!')
        expert_user.save()
        print(f"  Created expert user: {expert_user.username}")
    else:
        print(f"  Expert user already exists: {expert_user.username}")
    
    # Create Expert Profile for expert user
    print("Creating expert profiles...")
    expert_profile, created = Expert.objects.get_or_create(
        user=expert_user,
        defaults={
            'occupation': 'Software Engineer',
            'industry': industries[0],  # Technology
            'background': 'Senior software engineer with 10+ years of experience in full-stack development, specializing in React, Python, and cloud technologies.',
            'availability_status': 'available',
            'show_contact_info': True,
        }
    )
    if created:
        print(f"  Created expert profile for: {expert_user.username}")
    else:
        print(f"  Expert profile already exists for: {expert_user.username}")
    
    # Create Expertise records
    print("Creating expertise records...")
    expertise_data = [
        {
            'expert': expert_profile,
            'what_offering': 'Software development mentorship and career guidance',
            'who_would_benefit': 'Junior developers, career changers, and students looking to break into tech',
            'why_choose_you': 'I have successfully mentored 20+ developers and helped them land their dream jobs. I understand both the technical and career aspects of software development.',
            'skills_not_offered': 'I do not offer help with hardware engineering, game development, or mobile app development.'
        },
        {
            'expert': expert_profile,
            'what_offering': 'Technical interview preparation and coding practice',
            'who_would_benefit': 'Software engineers preparing for technical interviews at FAANG companies',
            'why_choose_you': 'I have conducted 100+ technical interviews and know exactly what companies are looking for. I can help you practice and improve your problem-solving skills.',
            'skills_not_offered': 'I do not offer help with system design interviews or behavioral interviews.'
        }
    ]
    
    for exp_data in expertise_data:
        expertise, created = Expertise.objects.get_or_create(
            expert=exp_data['expert'],
            what_offering=exp_data['what_offering'],
            defaults=exp_data
        )
        if created:
            print(f"  Created expertise: {exp_data['what_offering'][:50]}...")
        else:
            print(f"  Expertise already exists: {exp_data['what_offering'][:50]}...")
    
    print("\n✅ Test data creation completed!")
    print("\n📋 Test Accounts Created:")
    print("  Regular User:")
    print("    Username: testuser")
    print("    Email: test@example.com")
    print("    Password: TestPassword123!")
    print("    Role: member")
    print()
    print("  Admin User:")
    print("    Username: admin")
    print("    Email: admin@example.com")
    print("    Password: AdminPassword123!")
    print("    Role: admin")
    print()
    print("  Expert User:")
    print("    Username: expert")
    print("    Email: expert@example.com")
    print("    Password: ExpertPassword123!")
    print("    Role: member (with expert profile)")
    print()
    print("🌐 You can now test the application at:")
    print("  Frontend: http://localhost:3000")
    print("  Backend API: http://localhost:8000/api/")
    print("  Django Admin: http://localhost:8000/admin/")

if __name__ == "__main__":
    create_test_data()
