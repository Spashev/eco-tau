from collections import OrderedDict

from account import RoleType
from account.models import User
from utils.logger import log_exception


def get_user_role(user: User) -> str:
    try:
        role = ''

        if user.is_superuser:
            role = 'superuser'
        elif user.role == RoleType.ADMIN:
            role = RoleType.ADMIN
        elif user.role == RoleType.CLIENT:
            role = RoleType.CLIENT
        elif user.role == RoleType.MANAGER:
            role = RoleType.MANAGER
        elif user.role == RoleType.DIRECTOR:
            role = RoleType.DIRECTOR

        return role
    except Exception as e:
        log_exception(e, 'Error in get_user_role')
        return 'no_role'


def update_instance(instance, data) -> OrderedDict:
    for key, value in data.items():
        setattr(instance, key, value)
    instance.save()
