from django.db.models import Q

from kolibri.core.auth.constants import role_kinds
from kolibri.core.auth.models import Collection
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.models import Membership
from kolibri.core.auth.models import Role
from kolibri.core.chat.models import ConversationKind
from kolibri.core.device.models import DevicePermissions


def is_superadmin(user):
    return bool(getattr(user, "is_superuser", False))


def is_coach_or_admin(user, facility_id=None):
    if is_superadmin(user):
        return True
    roles = Role.objects.filter(
        user=user,
        kind__in=[role_kinds.ADMIN, role_kinds.COACH, role_kinds.ASSIGNABLE_COACH],
    )
    if facility_id:
        roles = roles.filter(collection__dataset__id=facility_id)
    return roles.exists()


def get_user_classrooms(user):
    """
    Returns classroom Collections where user is an enrolled student or an assigned coach.
    """
    if is_superadmin(user):
        return Collection.objects.filter(kind="classroom")

    # Enrolled as student
    enrolled_class_ids = Membership.objects.filter(
        user=user, collection__kind="classroom"
    ).values_list("collection_id", flat=True)

    # Assigned as coach
    coached_class_ids = Role.objects.filter(
        user=user,
        collection__kind="classroom",
        kind__in=[role_kinds.COACH, role_kinds.ASSIGNABLE_COACH],
    ).values_list("collection_id", flat=True)

    # Facility-wide coach/admin can access all classes in their facility
    facility_admin_facilities = Role.objects.filter(
        user=user,
        collection__kind="facility",
        kind__in=[role_kinds.ADMIN, role_kinds.COACH],
    ).values_list("collection_id", flat=True)

    q = Q(id__in=set(enrolled_class_ids).union(set(coached_class_ids)))
    if facility_admin_facilities:
        q |= Q(parent_id__in=facility_admin_facilities, kind="classroom")

    return Collection.objects.filter(q)


def can_message_user(sender, recipient):
    """
    Determines if sender is permitted to initiate/participate in 1:1 direct message with recipient.
    """
    if not sender or not recipient or not sender.is_authenticated:
        return False

    if sender.id == recipient.id:
        return True  # Can message self (notes to self)

    if is_superadmin(sender) or is_superadmin(recipient):
        return True

    # Check same facility
    if sender.facility_id != recipient.facility_id:
        return False

    sender_is_staff = is_coach_or_admin(sender)
    recipient_is_staff = is_coach_or_admin(recipient)

    # Staff can message any other staff in same facility
    if sender_is_staff and recipient_is_staff:
        return True

    # Staff can message students enrolled in classes they coach
    sender_classes = set(get_user_classrooms(sender).values_list("id", flat=True))
    recipient_classes = set(get_user_classrooms(recipient).values_list("id", flat=True))
    shared_classes = sender_classes.intersection(recipient_classes)

    if sender_is_staff or recipient_is_staff:
        return len(shared_classes) > 0

    # Student to Student: only allowed if they share at least one classroom
    return len(shared_classes) > 0


def get_eligible_contacts(user):
    """
    Returns query of FacilityUsers that the given user has permission to direct message.
    """
    if not user.is_authenticated:
        return FacilityUser.objects.none()

    if is_superadmin(user):
        return FacilityUser.objects.exclude(id=user.id)

    # Classrooms user belongs to
    user_classes = get_user_classrooms(user).values_list("id", flat=True)

    # Classmates: other students in same classes
    classmate_ids = Membership.objects.filter(
        collection_id__in=user_classes
    ).values_list("user_id", flat=True)

    # Teachers/coaches of those classes
    coach_ids = Role.objects.filter(
        collection_id__in=user_classes,
        kind__in=[role_kinds.COACH, role_kinds.ASSIGNABLE_COACH],
    ).values_list("user_id", flat=True)

    # Facility-wide coaches and admins
    facility_staff_ids = Role.objects.filter(
        collection_id=user.facility_id,
        kind__in=[role_kinds.ADMIN, role_kinds.COACH],
    ).values_list("user_id", flat=True)

    eligible_ids = (
        set(classmate_ids).union(set(coach_ids)).union(set(facility_staff_ids))
    )
    eligible_ids.discard(user.id)

    # Superadmins are also contactable
    superadmin_ids = DevicePermissions.objects.filter(is_superuser=True).values_list(
        "user_id", flat=True
    )
    eligible_ids.update(superadmin_ids)

    return (
        FacilityUser.objects.filter(id__in=eligible_ids)
        .order_by("full_name")
        .select_related("facility")
    )


def can_access_conversation(user, conversation):
    if not user.is_authenticated:
        return False

    if is_superadmin(user):
        return True

    if conversation.kind == ConversationKind.BROADCAST:
        if (
            conversation.facility_id is None
            or conversation.facility_id == user.facility_id
        ):
            return True
        return False

    if conversation.kind == ConversationKind.CLASSROOM:
        user_class_ids = set(get_user_classrooms(user).values_list("id", flat=True))
        return conversation.collection_id in user_class_ids

    # DIRECT conversation: user must be one of the participants
    return conversation.participants.filter(user=user).exists()
