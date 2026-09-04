from django.db.models import Q

from kolibri.core.auth.constants import role_kinds
from kolibri.core.auth.models import AnonymousUser
from kolibri.core.auth.permissions.base import BasePermissions
from kolibri.core.auth.permissions.base import q_none


class UserCanReadAssignment(BasePermissions):
    def user_can_create_object(self, user, obj):
        return False

    def user_can_read_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        return user.is_member_of(obj.collection) and obj.is_active

    def user_can_update_object(self, user, obj):
        return False

    def user_can_delete_object(self, user, obj):
        return False

    def readable_by_user_filter(self, user):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return q_none
        return Q(
            collection_id__in=user.memberships.all().values("collection_id"),
            is_active=True,
        )


class AssignmentSubmissionPermissions(BasePermissions):
    def user_can_create_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        assignment = getattr(obj, "assignment", None)
        if not assignment:
            return False
        # Learner creating own submission
        if user == getattr(obj, "learner", None):
            return user.is_member_of(assignment.collection) and assignment.is_active
        # Coach/admin
        return user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), assignment.collection
        )

    def user_can_read_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        if user == getattr(obj, "learner", None):
            return True
        assignment = getattr(obj, "assignment", None)
        if assignment:
            return user.has_role_for_collection(
                (role_kinds.ADMIN, role_kinds.COACH), assignment.collection
            )
        return False

    def user_can_update_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        assignment = getattr(obj, "assignment", None)
        if assignment and user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), assignment.collection
        ):
            return True
        if (
            user == getattr(obj, "learner", None)
            and getattr(obj, "status", "") != "graded"
        ):
            return True
        return False

    def user_can_delete_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        assignment = getattr(obj, "assignment", None)
        if assignment:
            return user.has_role_for_collection(
                (role_kinds.ADMIN, role_kinds.COACH), assignment.collection
            )
        return False

    def readable_by_user_filter(self, user):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return q_none
        from kolibri.core.auth.models import Role

        coach_collection_ids = Role.objects.filter(
            user=user,
            kind__in=(role_kinds.ADMIN, role_kinds.COACH),
        ).values("collection_id")
        return Q(learner=user) | Q(assignment__collection_id__in=coach_collection_ids)


class DiscussionThreadPermissions(BasePermissions):
    def user_can_create_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        return user.is_member_of(obj.collection) or user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), obj.collection
        )

    def user_can_read_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        return user.is_member_of(obj.collection) or user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), obj.collection
        )

    def user_can_update_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        if user == obj.created_by:
            return True
        return user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), obj.collection
        )

    def user_can_delete_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        if user == obj.created_by:
            return True
        return user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), obj.collection
        )

    def readable_by_user_filter(self, user):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return q_none
        from kolibri.core.auth.models import Role

        coach_collection_ids = Role.objects.filter(
            user=user,
            kind__in=(role_kinds.ADMIN, role_kinds.COACH),
        ).values("collection_id")
        member_collection_ids = user.memberships.all().values("collection_id")
        return Q(collection_id__in=member_collection_ids) | Q(
            collection_id__in=coach_collection_ids
        )


class DiscussionReplyPermissions(BasePermissions):
    def user_can_create_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        return user.is_member_of(obj.thread.collection) or user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), obj.thread.collection
        )

    def user_can_read_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        return user.is_member_of(obj.thread.collection) or user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), obj.thread.collection
        )

    def user_can_update_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        if user == obj.created_by:
            return True
        return user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), obj.thread.collection
        )

    def user_can_delete_object(self, user, obj):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False
        if user == obj.created_by:
            return True
        return user.has_role_for_collection(
            (role_kinds.ADMIN, role_kinds.COACH), obj.thread.collection
        )

    def readable_by_user_filter(self, user):
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return q_none
        from kolibri.core.auth.models import Role

        coach_collection_ids = Role.objects.filter(
            user=user,
            kind__in=(role_kinds.ADMIN, role_kinds.COACH),
        ).values("collection_id")
        member_collection_ids = user.memberships.all().values("collection_id")
        return Q(thread__collection_id__in=member_collection_ids) | Q(
            thread__collection_id__in=coach_collection_ids
        )
