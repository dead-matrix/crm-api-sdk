from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ServerRestartResult:
    message: str


@dataclass
class ServerStatusResult:
    """
    Готовность пользовательского воркера (GET /api/servers/status) — для
    опроса фактического завершения перезапуска, а не момента приёма
    команды open.

    bound — процесс слушает порт воркера (воркер запущен).
    up    — воркер отвечает на /ping/ (FastAPI поднят и обслуживает).
            Если up=True после рестарта — старый процесс (и его активные
            задачи) убит и заменён новым.
    """
    bound: bool
    up: bool

