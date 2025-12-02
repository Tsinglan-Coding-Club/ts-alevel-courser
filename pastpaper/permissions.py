TEACHER_GROUP_NAME = '教师'


def user_is_teacher(user):
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=TEACHER_GROUP_NAME).exists()


def has_question_editor_privileges(user):
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff or user_is_teacher(user)
