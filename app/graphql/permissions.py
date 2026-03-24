from typing import Any, Awaitable

from strawberry.permission import BasePermission
from strawberry.types import Info

from ..models import Task as TaskModel
from ..models import TaskLife as TaskLifeModel
from ..models import TaskLifeUser as TaskLifeUserModel
from ..models import RoleHouseUser as RoleHouseUserModel
from ..models import HouseUser as HouseUserModel

ADMIN_ROLE_ID = 1


class IsAuthenticated(BasePermission):
    message = "Not authenticated."

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        return bool(info.context.get("user_id"))


class IsHouseAdminForTask(BasePermission):
    """Checks that the authenticated user is an admin of the house the task belongs to.
    Expects `task_id` as a resolver argument."""

    message = "You must be an admin of the house this task belongs to."

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        user_id = info.context.get("user_id")
        task_id = kwargs.get("task_id")

        if not user_id or not task_id:
            return False

        db = info.context["db"]
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            return False

        role = db.query(RoleHouseUserModel).filter(
            RoleHouseUserModel.user_id == user_id,
            RoleHouseUserModel.house_id == task.house_id,
            RoleHouseUserModel.role_id == ADMIN_ROLE_ID,
        ).first()

        return role is not None


class IsHouseAdmin(BasePermission):
    """Checks that the authenticated user is an admin of a house.
    Expects `house_id` as a resolver argument."""

    message = "You must be an admin of this house."

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        user_id = info.context.get("user_id")
        house_id = kwargs.get("house_id")

        if not user_id or not house_id:
            return False

        db = info.context["db"]
        role = db.query(RoleHouseUserModel).filter(
            RoleHouseUserModel.user_id == user_id,
            RoleHouseUserModel.house_id == house_id,
            RoleHouseUserModel.role_id == ADMIN_ROLE_ID,
        ).first()

        return role is not None


class IsTaskBelongToThisUser(BasePermission):
    """Checks that the authenticated user or the user_id provided correctly belongs to the task and this house.
    Expects `house_id`, `task_id` and `user_id` (optional) as a resolver argument."""

    message = "The user is not attached to this tasked"

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        user_id = kwargs.get("user_id") if kwargs.get("user_id") is not None else info.context.get("user_id")
        task_id = kwargs.get("task_id")

        if not user_id or not task_id:
            return False

        db = info.context["db"]
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            return False

        house_id = task.house_id

        # Admins can act on any task in their house
        is_admin = db.query(RoleHouseUserModel).filter(
            RoleHouseUserModel.user_id == info.context.get("user_id"),
            RoleHouseUserModel.house_id == house_id,
            RoleHouseUserModel.role_id == ADMIN_ROLE_ID,
        ).first()
        if is_admin:
            return True

        house_user = db.query(HouseUserModel).filter(
            HouseUserModel.house_id == house_id,
            HouseUserModel.user_id == user_id,
        ).first()

        if not house_user:
            return False

        task_life = db.query(TaskLifeModel).filter(TaskLifeModel.task_id == task_id).first()
        if not task_life:
            return False

        assigned = db.query(TaskLifeUserModel).filter(
            TaskLifeUserModel.task_life_id == task_life.id,
            TaskLifeUserModel.user_id == user_id,
        ).first()

        return assigned is not None


class IsTaskBelongToTheUserHouse(BasePermission):
    """Checks if this task is attached to the current userHouse.
    Expects `task_id`as a resolver argument."""

    message = "This task do not belong to this house"

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        user_id = info.context.get("user_id")
        task_id = kwargs.get("task_id")

        if not user_id or not task_id:
            return False

        db = info.context["db"]
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            return False

        house_id = task.house_id
        HouseUser = db.query(HouseUserModel).filter(HouseUserModel.house_id == house_id,
                                                    HouseUserModel.user_id == user_id).first()

        if not HouseUser:
            return False

        return True
