from datetime import datetime

def get_start_end(current_started_at: datetime, current_ended_at: datetime, new_started_at: datetime, new_ended_at: datetime) -> tuple[datetime, datetime]:

    if new_started_at is not None and (current_started_at is None or new_started_at < current_started_at):
        current_started_at = new_started_at

    if new_ended_at is not None and (current_ended_at is None or new_ended_at > current_ended_at):
        current_ended_at = new_ended_at

    return (current_started_at, current_ended_at)