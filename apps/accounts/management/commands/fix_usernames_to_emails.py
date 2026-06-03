from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Set each user.username to their email address (dry-run by default). Use --commit to apply changes.'

    def add_arguments(self, parser):
        parser.add_argument('--commit', action='store_true', help='Apply changes to the database')

    def handle(self, *args, **options):
        from apps.accounts.models import CustomUser
        users = CustomUser.objects.all()
        changed = 0
        for u in users:
            if not u.email:
                self.stdout.write(self.style.WARNING(f'SKIP (no email): {u.username} (id={u.pk})'))
                continue
            if u.username != u.email:
                self.stdout.write(f"Will update: id={u.pk} username='{u.username}' -> '{u.email}'")
                if options['commit']:
                    u.username = u.email
                    u.save(update_fields=['username'])
                    changed += 1
        if options['commit']:
            self.stdout.write(self.style.SUCCESS(f'Updated {changed} user(s).'))
        else:
            self.stdout.write(self.style.NOTICE('Dry run complete. Rerun with --commit to apply changes.'))
