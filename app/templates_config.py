import time
from datetime import UTC, datetime

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")


def _format_duration(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    hours, rem = divmod(int(seconds), 3600)
    minutes = rem // 60
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m"
    return f"{int(seconds)}s"


def _relative_time(epoch: int | float | None) -> str:
    if epoch is None:
        return "—"
    delta = int(time.time() - epoch)
    if delta < 60:
        return "just now"
    if delta < 3600:
        return f"{delta // 60}m ago"
    if delta < 86400:
        return f"{delta // 3600}h ago"
    return f"{delta // 86400}d ago"


def _date_fmt(epoch: int | None, fmt: str = "%B %d, %Y") -> str:
    if epoch is None:
        return "—"
    return datetime.fromtimestamp(epoch, tz=UTC).strftime(fmt)


templates.env.filters["duration"] = _format_duration
templates.env.filters["relative"] = _relative_time
templates.env.filters["date_fmt"] = _date_fmt
