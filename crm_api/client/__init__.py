from __future__ import annotations

from .base import BaseCRMClient
from .users import UsersAPI
from .accounts import AccountsAPI
from .catalog import CatalogAPI
from .departments import DepartmentsAPI
from .dialogs import DialogsAPI
from .notes import NotesAPI
from .payments import PaymentsAPI
from .prompts import PromptsAPI
from .proxy import ProxyAPI
from .referrals import ReferralsAPI
from .servers import ServersAPI
from .staff import StaffAPI
from .tasks import TasksAPI
from .scripts import ScriptsAPI
from .profile import ProfileAPI
from .subscriptions import SubscriptionsAPI
from .activation import ActivationAPI



class CRMApiClient(
    BaseCRMClient,
    UsersAPI,
    AccountsAPI,
    CatalogAPI,
    DepartmentsAPI,
    DialogsAPI,
    NotesAPI,
    PaymentsAPI,
    PromptsAPI,
    ProxyAPI,
    ReferralsAPI,
    ServersAPI,
    StaffAPI,
    TasksAPI,
    ScriptsAPI,
    ProfileAPI,
    SubscriptionsAPI,
    ActivationAPI,
):
    """Комбинированный клиент CRM-API: базовый клиент + API по доменам."""


__all__ = ["CRMApiClient"]

