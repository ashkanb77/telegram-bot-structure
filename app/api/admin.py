from sqladmin import ModelView

from app.models import Subscription
from app.models.message import Message
from app.models.plan import Plan
from app.models.user import User


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = [
        User.id,
        User.username,
        User.first_name,
        User.last_name,
        User.created_at
    ]

    column_details_list = [
        User.id,
        User.username,
        User.first_name,
        User.last_name,
        User.chat_id,
        User.subscriptions,
        User.messages,
    ]

    column_searchable_list = [
        User.id,
        User.username,
        User.first_name,
        User.chat_id,
        User.telegram_id
    ]

    column_sortable_list = [
        User.id,
        User.username,
        User.created_at,
    ]

    form_excluded_columns = [
        User.id,
        User.created_at,
        User.updated_at,
    ]

    can_create = True
    can_edit = True
    can_delete = True

    column_default_sort = (User.username, True)


class MessageAdmin(ModelView, model=Message):
    name = "Message"
    name_plural = "Messages"
    icon = "fa-solid fa-envelope"

    column_list = [
        Message.id,
        Message.user_id,
        Message.used_tokens,
        Message.model,
        Message.content,
        Message.answer,
        Message.answered_at,
        Message.telegram_message_id,
    ]

    column_details_list = [
        Message.id,
        Message.user_id,
        Message.used_tokens,
        Message.model,
        Message.content,
        Message.answer,
        Message.answered_at,
        Message.telegram_message_id,
    ]

    column_searchable_list = [
        Message.content,
        Message.answer,
        Message.user_id
    ]

    column_sortable_list = [
        Message.id,
        Message.answered_at,
        Message.used_tokens,
    ]

    column_formatters = {
        Message.answered_at: lambda value, model: value.answered_at.strftime(
            "%Y-%m-%d %H:%M:%S") if value and value.answered_at else "—",
    }

    form_excluded_columns = [
        Message.id,
        Message.created_at,
        Message.updated_at,
    ]

    column_default_sort = (Message.answered_at, True)

    can_create = True
    can_delete = True
    can_edit = True


class PlanAdmin(ModelView, model=Plan):
    name = "Plan"
    name_plural = "Plans"
    icon = "fa-solid fa-user"

    column_list = [
        Plan.id,
        Plan.name,
        Plan.price,
        Plan.tokens,
        Plan.is_active,
        Plan.sort_order
    ]

    column_details_list = [
        Plan.id,
        Plan.name,
        Plan.price,
        Plan.tokens,
        Plan.is_active,
        Plan.sort_order,
        Plan.description
    ]

    column_sortable_list = [
        Plan.id,
        Plan.sort_order,
        Plan.price,
        Plan.tokens
    ]

    column_searchable_list = [
        Plan.id, Plan.name,
    ]

    form_excluded_columns = [
        Plan.id,
        Plan.created_at,
        Plan.updated_at,
    ]

    can_create = True
    can_edit = True
    can_delete = True

    column_default_sort = (Plan.created_at, True)


class SubscriptionAdmin(ModelView, model=Subscription):
    name = "Subscription"
    name_plural = "Subscriptions"
    icon = "fa-solid fa-user"

    column_list = [
        Subscription.used_tokens,
        Subscription.status,
        Subscription.expires_at,
        Subscription.activated_at,
        Subscription.user_id,
        Subscription.plan_id,
    ]

    column_details_list = [
        Subscription.used_tokens,
        Subscription.status,
        Subscription.expires_at,
        Subscription.activated_at,
        Subscription.user_id,
        Subscription.plan_id,
    ]

    column_sortable_list = [
        Subscription.used_tokens,
        Subscription.status,
        Subscription.expires_at,
        Subscription.activated_at,
    ]

    column_searchable_list = [
        Subscription.user_id, Subscription.plan_id,
    ]

    form_excluded_columns = [
        Subscription.id,
        Subscription.created_at,
        Subscription.updated_at,
    ]

    can_create = True
    can_edit = True
    can_delete = True

    column_default_sort = (Subscription.expires_at, False)
