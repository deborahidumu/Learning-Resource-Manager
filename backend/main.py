# backend/main.py
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pydantic import ValidationError

from api.auth import router as auth_router
from api.admin import router as admin_router
from core.security import admin_required
from db.conn import db_conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_conn.start_connection()

    yield

    await db_conn.close_connection()


app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    errors = {}

    error_list = exc.errors() if hasattr(exc, "errors") else []

    for error in error_list:
        # Get field name
        loc = error.get("loc", [])
        field = loc[-1] if loc else "general"

        # Get error message - strip technical details
        message = error.get("msg", "Unknown error")
        if " [type=" in message:
            message = message.split(" [type=")[0]

        # Add to errors dict
        if field not in errors:
            errors[field] = []
        errors[field].append(message)

    # If no errors were processed, use fallback
    if not errors:
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Validation error",
                "errors": {"general": ["Invalid input data"]},
            },
        )

    return JSONResponse(
        status_code=400,
        content={"status": "error", "detail": "Validation error", "errors": errors},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error", 
            "detail": exc.detail,
            "errors": {"general": [exc.detail]}
        },
    )


app.include_router(auth_router, tags=["Auth"])
app.include_router(admin_router, tags=["Admin"], dependencies=[Depends(admin_required)])
