#!/usr/bin/env python
"""Utility script to create or update a teacher account with question editing permissions."""
import argparse
import getpass
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django
    django.setup()
except Exception as exc:  # pragma: no cover - defensive import guard
    print(f"Failed to initialise Django: {exc}")
    sys.exit(1)

from django.contrib.auth.models import Group, Permission, User  # noqa: E402
from django.contrib.contenttypes.models import ContentType  # noqa: E402

from pastpaper.models import Question  # noqa: E402
from pastpaper.permissions import TEACHER_GROUP_NAME  # noqa: E402


QUESTION_PERMISSIONS = ['add_question', 'change_question', 'delete_question', 'view_question']


def ensure_teacher_group():
    """Ensure the teacher group exists and has the required permissions."""
    group, _ = Group.objects.get_or_create(name=TEACHER_GROUP_NAME)
    question_ct = ContentType.objects.get_for_model(Question)
    perms = list(Permission.objects.filter(content_type=question_ct, codename__in=QUESTION_PERMISSIONS))
    group.permissions.set(perms)
    return group, len(perms)


def ensure_teacher_user(username, email, password, group):
    """Create or update the teacher user and attach the group."""
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    if email:
        user.email = email
    if password:
        user.set_password(password)
    user.is_active = True
    user.save()
    user.groups.add(group)
    return user, created


def parse_args():
    parser = argparse.ArgumentParser(description='Create or update a teacher account with question editing rights.')
    parser.add_argument('--username', required=True, help='Username for the teacher account')
    parser.add_argument('--email', default='', help='Email for the teacher account')
    parser.add_argument('--password', default=None, help='Password for the teacher account; prompted if omitted')
    return parser.parse_args()


def main():
    args = parse_args()
    password = args.password or getpass.getpass('Password for teacher account: ')
    if not password:
        print('Password is required.')
        sys.exit(1)

    group, perm_count = ensure_teacher_group()
    user, created = ensure_teacher_user(args.username, args.email, password, group)

    action = 'created' if created else 'updated'
    print(f"Teacher group '{TEACHER_GROUP_NAME}' ensured with {perm_count} permissions.")
    print(f"User '{user.username}' {action} and added to '{TEACHER_GROUP_NAME}' group.")


if __name__ == '__main__':
    main()
