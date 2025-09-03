from requests_ratelimiter import LimiterSession
from datetime import datetime


# Quota configuration
QUOTA_DAY_GET_PER_MINUTE = 60
QUOTA_DAY_OTHER_PER_MINUTE = 10
QUOTA_NIGHT_GET_PER_MINUTE = 200
QUOTA_NIGHT_OTHER_PER_MINUTE = 50
DAY_START_HOUR = 6
DAY_END_HOUR = 20

# Cache token configuration
TIMEOUT_TOKEN = 3600
SAFETY_MARGIN = 60

session_get_day = LimiterSession(per_minute=QUOTA_DAY_GET_PER_MINUTE)
session_write_day = LimiterSession(per_minute=QUOTA_DAY_OTHER_PER_MINUTE)
session_get_night = LimiterSession(per_minute=QUOTA_NIGHT_GET_PER_MINUTE)
session_write_night = LimiterSession(per_minute=QUOTA_NIGHT_OTHER_PER_MINUTE)


def is_night() -> bool:
    """Retourne True si l'heure courante est entre 20h et 6h."""
    hour = datetime.now().hour
    return hour > DAY_END_HOUR or hour < DAY_START_HOUR


def get_session_get() -> LimiterSession:
    """Retourne la session GET adaptée à l'heure courante."""
    return session_get_night if is_night() else session_get_day


def get_session_write() -> LimiterSession:
    """Retourne la session WRITE adaptée à l'heure courante."""
    return session_write_night if is_night() else session_write_day
