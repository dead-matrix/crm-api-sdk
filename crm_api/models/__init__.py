from __future__ import annotations

# Inputs
from .inputs import (
    ActionType,
    PaymentProvider,
    PaymentMethod,
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
from .dialogs import DialogItem, TransferDialogResult, StatusItem, StatusesResult, ChangeStatusResult, DialogSearchItem, DialogSearchResult
from .notes import NoteItem, NoteStaff

# Payments
from .payments import (
    CalcItem,
    PaymentsCalculateResult,
    InvoiceDraftResult,
    InvoiceIssueResult,
    ActivationLink,
    PaymentHistoryItem,
    PaymentsListResult,
    ConfirmPaymentResult,
    RefundResult,
    InvoiceInfoResult,
    Sale,
    MonthlySalesResult,
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
    ExtendAccessResult,
    ExtendAiLimitResult,
    ListUserItem,
    ListUsersResult,
)

# Subscriptions
from .subscriptions import (
    AccessPaymentRef,
    AccessStaffRef,
    AccessHistoryItem,
    SubscriptionsHistoryResult,
    AccessDefinitionsResult,
    TransferLinkResult,
    TransferRedeemInput,
    TransferRedeemResult,
)

# Activation
from .activation import (
    ActivationRedeemInput,
    ActivationRedeemResult,
)

# Tasks
from .tasks import TaskListItem, TaskInfoResult, TaskLogResult, ActiveTasksResult

# Sales decks (legacy ScriptItem / ScriptFull удалены в Phase 5 — для
# текстовых быстрых ответов используется ReplyTemplateFull ниже).
from .scripts import PriceMediaItem, ToolsMediaItem, ToolsMediaResult

# Reply templates (multimedia quick replies)
from .reply_templates import (
    ReplyTemplateCreator,
    ReplyTemplatePreview,
    ReplyTemplateListItem,
    ReplyTemplateItem,
    ReplyTemplateFull,
    DeleteReplyTemplateResult,
    REPLY_TEMPLATE_KIND_SINGLE,
    REPLY_TEMPLATE_KIND_ALBUM,
    REPLY_TEMPLATE_ITEM_TYPE_TEXT,
    REPLY_TEMPLATE_ITEM_TYPE_PHOTO,
    REPLY_TEMPLATE_ITEM_TYPE_VIDEO,
    REPLY_TEMPLATE_ITEM_TYPE_GIF,
    REPLY_TEMPLATE_ITEM_TYPE_VOICE,
    REPLY_TEMPLATE_ITEM_TYPE_VIDEO_NOTE,
    REPLY_TEMPLATE_ITEM_TYPE_STICKER,
    REPLY_TEMPLATE_ITEM_TYPE_FILE,
    REPLY_TEMPLATE_ITEM_TYPES,
    REPLY_TEMPLATE_ALBUM_ITEM_TYPES,
    REPLY_TEMPLATE_NO_CAPTION_ITEM_TYPES,
    REPLY_TEMPLATE_TITLE_MAX_LENGTH,
    REPLY_TEMPLATE_CAPTION_MAX,
    REPLY_TEMPLATE_ALBUM_MIN_ITEMS,
    REPLY_TEMPLATE_ALBUM_MAX_ITEMS,
    REPLY_TEMPLATE_ITEM_MAX_POS,
)

__all__ = [
    # Inputs
    "ActionType",
    "PaymentProvider",
    "PaymentMethod",
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
    "DialogSearchItem",
    "DialogSearchResult",
    "NoteItem",
    "NoteStaff",
    # Payments
    "CalcItem",
    "PaymentsCalculateResult",
    "InvoiceDraftResult",
    "InvoiceIssueResult",
    "ActivationLink",
    "PaymentHistoryItem",
    "PaymentsListResult",
    "ConfirmPaymentResult",
    "RefundResult",
    "InvoiceInfoResult",
    "Sale",
    "MonthlySalesResult",
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
    "ExtendAccessResult",
    "ExtendAiLimitResult",
    "ListUserItem",
    "ListUsersResult",
    # Subscriptions
    "AccessPaymentRef",
    "AccessStaffRef",
    "AccessHistoryItem",
    "SubscriptionsHistoryResult",
    "AccessDefinitionsResult",
    "TransferLinkResult",
    "TransferRedeemInput",
    "TransferRedeemResult",
    # Activation
    "ActivationRedeemInput",
    "ActivationRedeemResult",
    # Tasks
    "TaskListItem",
    "TaskInfoResult",
    "TaskLogResult",
    "ActiveTasksResult",
    # Sales decks
    "PriceMediaItem",
    "ToolsMediaItem",
    "ToolsMediaResult",
    # Reply templates
    "ReplyTemplateCreator",
    "ReplyTemplatePreview",
    "ReplyTemplateListItem",
    "ReplyTemplateItem",
    "ReplyTemplateFull",
    "DeleteReplyTemplateResult",
    "REPLY_TEMPLATE_KIND_SINGLE",
    "REPLY_TEMPLATE_KIND_ALBUM",
    "REPLY_TEMPLATE_ITEM_TYPE_TEXT",
    "REPLY_TEMPLATE_ITEM_TYPE_PHOTO",
    "REPLY_TEMPLATE_ITEM_TYPE_VIDEO",
    "REPLY_TEMPLATE_ITEM_TYPE_GIF",
    "REPLY_TEMPLATE_ITEM_TYPE_VOICE",
    "REPLY_TEMPLATE_ITEM_TYPE_VIDEO_NOTE",
    "REPLY_TEMPLATE_ITEM_TYPE_STICKER",
    "REPLY_TEMPLATE_ITEM_TYPE_FILE",
    "REPLY_TEMPLATE_ITEM_TYPES",
    "REPLY_TEMPLATE_ALBUM_ITEM_TYPES",
    "REPLY_TEMPLATE_NO_CAPTION_ITEM_TYPES",
    "REPLY_TEMPLATE_TITLE_MAX_LENGTH",
    "REPLY_TEMPLATE_CAPTION_MAX",
    "REPLY_TEMPLATE_ALBUM_MIN_ITEMS",
    "REPLY_TEMPLATE_ALBUM_MAX_ITEMS",
    "REPLY_TEMPLATE_ITEM_MAX_POS",
]

