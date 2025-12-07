from __future__ import annotations

# Inputs
from .inputs import (
    ActionType,
    CreateUserInput,
    UpdateUserInput,
    AddAccessInput,
    PaymentsCalculateInput,
    InvoiceDraftInput,
    InvoiceIssueInput,
    RefundInput,
)

# Accounts/Profile
from .accounts import (
    DayTotal,
    AccountItem,
    ProfileStatistics,
    PosterAccount,
    PosterSubscription,
    Bot3Summary,
)

# Catalog/Departments/Dialogs/Notes
from .catalog import ProductEntry, CategoryBucket
from .departments import DepartmentItem
from .dialogs import DialogItem, TransferDialogResult, StatusItem, StatusesResult, ChangeStatusResult
from .notes import NoteItem, NoteStaff

# Payments
from .payments import (
    CalcItem,
    PaymentsCalculateResult,
    InvoiceDraftResult,
    InvoiceIssueResult,
    ActivationLink,
    PaymentHistoryItem,
    ConfirmPaymentResult,
    RefundResult,
    InvoiceInfoResult,
)

# Prompt
from .prompts import PromptUpdateResult

# Proxy
from .proxy import ProxyCheckItem, ProxyCheckResult, ProxyItem

# Referrals
from .referrals import ReferreePayment, ReferreeInfo, ReferralsInfoResult

# Servers
from .servers import ServerRestartResult

# Staff
from .staff import StaffInfo

# Users
from .users import (
    UserBotInfo,
    GetUserResult,
    CreateUserResult,
    UpdateUserResult,
    AddAccessResult,
)

# Subscriptions
from .subscriptions import (
    AccessPaymentRef,
    AccessStaffRef,
    AccessHistoryItem,
    SubscriptionsHistoryResult,
    AccessDefinitionsResult,
    TransferLinkResult,
)

# Tasks
from .tasks import TaskListItem, TaskInfoResult, TaskLogResult

# Scripts
from .scripts import ScriptItem, ScriptFull, PriceMediaItem, ToolsMediaResult

__all__ = [
    # Inputs
    "ActionType",
    "CreateUserInput",
    "UpdateUserInput",
    "AddAccessInput",
    "PaymentsCalculateInput",
    "InvoiceDraftInput",
    "InvoiceIssueInput",
    "RefundInput",
    # Accounts/Profile
    "DayTotal",
    "AccountItem",
    "ProfileStatistics",
    "PosterAccount",
    "PosterSubscription",
    "Bot3Summary",
    # Catalog/Departments/Dialogs/Notes
    "ProductEntry",
    "CategoryBucket",
    "DepartmentItem",
    "DialogItem",
    "TransferDialogResult",
    "StatusItem",
    "StatusesResult",
    "ChangeStatusResult",
    "NoteItem",
    "NoteStaff",
    # Payments
    "CalcItem",
    "PaymentsCalculateResult",
    "InvoiceDraftResult",
    "InvoiceIssueResult",
    "ActivationLink",
    "PaymentHistoryItem",
    "ConfirmPaymentResult",
    "RefundResult",
    "InvoiceInfoResult",
    # Prompt
    "PromptUpdateResult",
    # Proxy
    "ProxyCheckItem",
    "ProxyCheckResult",
    "ProxyItem",
    # Referrals
    "ReferreePayment",
    "ReferreeInfo",
    "ReferralsInfoResult",
    # Servers
    "ServerRestartResult",
    # Staff
    "StaffInfo",
    # Users
    "UserBotInfo",
    "GetUserResult",
    "CreateUserResult",
    "UpdateUserResult",
    "AddAccessResult",
    # Subscriptions
    "AccessPaymentRef",
    "AccessStaffRef",
    "AccessHistoryItem",
    "SubscriptionsHistoryResult",
    "AccessDefinitionsResult",
    "TransferLinkResult",
    # Tasks
    "TaskListItem",
    "TaskInfoResult",
    "TaskLogResult",
    # Scripts
    "ScriptItem",
    "ScriptFull",
    "PriceMediaItem",
    "ToolsMediaResult",
]

