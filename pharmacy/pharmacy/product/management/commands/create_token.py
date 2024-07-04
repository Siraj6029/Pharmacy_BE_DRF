# your_chosen_app/management/commands/create_token.py

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


class Command(BaseCommand):
    help = "Generate a token for a specific user"

    def add_arguments(self, parser):
        parser.add_argument(
            "username", type=str, help="Username for which to generate the token"
        )

    def handle(self, *args, **options):
        username = options["username"]
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            raise CommandError(f'User "{username}" does not exist')

        refresh = RefreshToken.for_user(user)
        self.stdout.write(
            self.style.SUCCESS(f"Token created for {username}: {refresh.access_token}")
        )
