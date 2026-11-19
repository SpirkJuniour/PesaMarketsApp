from django.core.management.base import BaseCommand
from django.conf import settings
from markets.services.notification_service import send_otp_email

class Command(BaseCommand):
    help = "Test real Gmail SMTP delivery to a specified email address"

    def add_arguments(self, parser):
        parser.add_argument('recipient', type=str, help='Recipient email address (e.g. user@gmail.com)')

    def handle(self, *args, **options):
        recipient = options['recipient'].strip()
        self.stdout.write(f"Testing Gmail SMTP connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
        self.stdout.write(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER or '(Not configured in .env)'}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

        res = send_otp_email(recipient_email=recipient, otp_code='849201', user_name='Trader', purpose='login')
        if res.get('sent'):
            self.stdout.write(self.style.SUCCESS(f"SUCCESS: Real verification email successfully dispatched to {recipient}! Check inbox & spam."))
        else:
            self.stdout.write(self.style.ERROR(f"DELIVERY FAILED: Could not dispatch email to {recipient}."))
            self.stdout.write(self.style.WARNING(f"Reason: {res.get('error')}"))
            self.stdout.write(self.style.NOTICE("To fix: Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in your .env file."))
