from django.core.management.base import BaseCommand

from mensa_member_connect.models.custom_user import CustomUser
from mensa_member_connect.utils.image_utils import compress_profile_photo_bytes


class Command(BaseCommand):
    help = "Compress existing user profile photos in the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without saving.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        users = CustomUser.objects.filter(profile_photo__isnull=False).only("id", "profile_photo")

        scanned = 0
        changed = 0
        skipped = 0
        bytes_before = 0
        bytes_after = 0

        for user in users.iterator():
            scanned += 1
            original = bytes(user.profile_photo)
            original_size = len(original)
            bytes_before += original_size

            try:
                compressed = compress_profile_photo_bytes(original)
            except Exception as exc:
                skipped += 1
                self.stdout.write(
                    self.style.WARNING(f"Skipped user {user.id}: {exc}")
                )
                continue

            compressed_size = len(compressed)
            bytes_after += min(original_size, compressed_size)

            # Keep existing if compression does not reduce size.
            if compressed_size >= original_size:
                skipped += 1
                continue

            changed += 1
            if not dry_run:
                user.profile_photo = compressed
                user.save(update_fields=["profile_photo"])

        saved_bytes = bytes_before - bytes_after
        saved_mb = saved_bytes / (1024 * 1024)

        mode = "DRY RUN" if dry_run else "APPLIED"
        self.stdout.write(self.style.SUCCESS(f"[{mode}] Scanned: {scanned}"))
        self.stdout.write(self.style.SUCCESS(f"[{mode}] Updated: {changed}"))
        self.stdout.write(self.style.SUCCESS(f"[{mode}] Skipped: {skipped}"))
        self.stdout.write(
            self.style.SUCCESS(
                f"[{mode}] Estimated bytes saved: {saved_bytes} ({saved_mb:.2f} MB)"
            )
        )
