import os

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import User


class Command(BaseCommand):
    """Create or update a single administrator account outside the public registration flow.

    Administrator self-registration requires ADMIN_REGISTRATION_CODE, which is
    normally left unset. This command is the supported way to get an admin
    login instead: it creates one fixed account directly, or resets its
    password if the account already exists.
    """

    help = "Create or reset the one administrator account (bypasses public registration)."

    def add_arguments(self, parser):
        parser.add_argument("--email", default=os.environ.get("ADMIN_SEED_EMAIL", ""))
        parser.add_argument("--password", default=os.environ.get("ADMIN_SEED_PASSWORD", ""))
        parser.add_argument("--first-name", default=os.environ.get("ADMIN_SEED_FIRST_NAME", "Admin"))
        parser.add_argument("--last-name", default=os.environ.get("ADMIN_SEED_LAST_NAME", "User"))

    def handle(self, *args, **options):
        email = User.objects.normalize_email(options["email"]).lower().strip() if options["email"] else ""
        password = options["password"]
        if not email or not password:
            raise CommandError(
                "Both --email and --password are required "
                "(or set ADMIN_SEED_EMAIL / ADMIN_SEED_PASSWORD)."
            )

        try:
            password_validation.validate_password(password)
        except DjangoValidationError as exc:
            raise CommandError("; ".join(exc.messages)) from exc

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": options["first_name"],
                "last_name": options["last_name"],
                "role": User.Role.ADMINISTRATOR,
                "is_active": True,
            },
        )
        user.role = User.Role.ADMINISTRATOR
        user.is_active = True
        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} administrator account: {email}"))
