from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter instance shared across the app and routers
limiter = Limiter(key_func=get_remote_address)
