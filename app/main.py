import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .errors.errors import ApiError
from .routers import company

app = FastAPI()
app.include_router(company.router)
version = "1.0"

@app.get("/health")
async def health():
    return {"status": "OK"}

@app.exception_handler(ApiError)
async def api_error_exception_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.code,
        content={
            "mssg": exc.description, 
            "details": str(exc),
            "version": version
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        error_detail = {
            "location": error["loc"],
            "message": error["msg"],
            "type": error["type"]
        }
        errors.append(error_detail)

    return JSONResponse(
        status_code=400,
        content={
            "message": "Validation Error",
            "details": errors,
            "version": version
        },
    )