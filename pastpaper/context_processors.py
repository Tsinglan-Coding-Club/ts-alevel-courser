from .permissions import has_question_editor_privileges, TEACHER_GROUP_NAME


def permissions(request):
    user = getattr(request, 'user', None)
    return {
        'can_create_questions': has_question_editor_privileges(user),
        'teacher_group_name': TEACHER_GROUP_NAME,
    }
