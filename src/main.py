from fastapi import FastAPI
from fastapi.security import HTTPBasic
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .limiter.limiter import limiter
from .routes.login import auth
from .routes.protected_resource import protected_resource
from .routes.resources import resource


security = HTTPBasic()


app = FastAPI()
app.include_router(auth)
app.include_router(resource)
app.include_router(protected_resource)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
