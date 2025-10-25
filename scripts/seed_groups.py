"""
seed_groups.py

This script seeds the LocalGroup model in your Django project using data
from a CSV file (localgroup.txt). Place this script and the CSV file together
in the same folder (e.g., root/scripts/). Run with:

    python seed_groups.py

It will create LocalGroup entries if they do not already exist.

Notes:
- The script strips any trailing ' - XXX' from the group name.
- Ensure your Django settings module is correctly set for your project.
"""

import csv
import os
import django

# Make the script path-independent
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, "localgroup.txt")

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mensa_member_connect_backend.settings")
django.setup()

from mensa_member_connect.models.local_group import LocalGroup

with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if not row or len(row) < 2:
            continue  # skip empty or malformed lines

        group_number, group_name = row

        # Optionally strip trailing ' - XXX' if present
        if " - " in group_name:
            group_name = group_name.split(" - ")[0]

        try:
            lg, created = LocalGroup.objects.get_or_create(
                group_number=group_number.strip(),
                defaults={"group_name": group_name.strip()},
            )
            if created:
                print(f"✅ Created {group_name.strip()} ({group_number.strip()})")
            else:
                print(f"ℹ️ Already exists {group_name.strip()} ({group_number.strip()})")
        except Exception as e:
            print(f"❌ Failed {group_name.strip()} ({group_number.strip()}): {e}")
