from fastapi import Request


async def get_client_ip(request: Request) -> str:
    """
    Get client IP from request object
    """
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.client.host
    return ip
