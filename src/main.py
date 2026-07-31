from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.routes import router as expenses_router

app = FastAPI(
    title="Smart Expense Tracker API",
    description=(
        "REST API to manage personal expenses, supporting CRUD operations, "
        "category filtering, and overall/by-category totals calculation. "
        "Built with FastAPI and Pydantic for high performance and OpenAPI documentation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for flexible integration with frontend or testing tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Standardize validation error responses with clear RFC-style structure.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request - Invalid or malformed input data",
            "detail": jsonable_encoder(exc.errors()),
            "code": 400
        }
    )


# Include main expenses router
app.include_router(expenses_router)


@app.get("/", tags=["Health"])
def health_check():
    """
    Root health check endpoint.
    """
    return {
        "status": "ok",
        "service": "Smart Expense Tracker API",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
