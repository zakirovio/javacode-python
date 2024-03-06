from rest_framework.exceptions import ValidationError
from redis import Redis


def check_access_token(token: str, cache: Redis) -> bool | int:
    """Simple temporary checker"""
    if cache.get('accessBlacklist') is not None:
        try:
            bl_set = cache.get("accessBlacklist")
            if token in bl_set:
                return False
            else:
                return True
        finally:
            cache.close()
    return 1
