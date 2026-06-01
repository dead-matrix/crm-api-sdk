from __future__ import annotations

from ..exceptions import ApiError, AuthError, ConfigError, ValidationError
from ..models import (
    ActivationRedeemInput,
    ActivationRedeemResult,
)
from ..utils import parse_dt


class ActivationAPI:
    async def activation_redeem(
        self, data: ActivationRedeemInput
    ) -> ActivationRedeemResult:
        """
        Активировать ACT_-токен (deep-link, выданный после оплаты).

        Не выбрасывает исключение на известные бизнес-коды (already_used,
        invalid_token, expired, not_found, wrong_bot, wrong_recipient,
        revoked) — возвращает ActivationRedeemResult(success=False).

        Сервер маркирует бизнес-ошибки HTTP-статусами 400/403/404/409/422,
        поэтому ловим всё семейство ApiError/AuthError/ValidationError —
        у каждого из них есть атрибут `code`.

        Транспортные/системные ошибки (HttpError, ConfigError) выбрасываются.
        """
        if (
            not data.token
            or data.recipient_user_id <= 0
            or data.bot_id <= 0
        ):
            raise ConfigError(
                "token, recipient_user_id and bot_id must be provided"
            )
        body = {
            "token": str(data.token),
            "recipient_user_id": int(data.recipient_user_id),
            "bot_id": int(data.bot_id),
        }
        try:
            d = await self._post(
                "/api/activation/redeem",
                json_body=body,
                need_auth=True,
            )
        except (ApiError, AuthError, ValidationError) as e:
            return ActivationRedeemResult(
                success=False,
                error_code=e.code,
                error_message=str(e) or e.code,
            )
        return ActivationRedeemResult(
            success=True,
            user_id=d.get("user_id"),
            bot_id=d.get("bot_id"),
            action=d.get("action"),
            access=d.get("access"),
            access_end=parse_dt(d.get("access_end")),
            quantity=d.get("quantity"),
            activation_code_id=d.get("activation_code_id"),
            payment_id=d.get("payment_id"),
        )
