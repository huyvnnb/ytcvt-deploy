from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


from app.schema import ModelResponse, ErrorDetail, ErrorResponse


class ServiceError(Exception):
    """Lớp Exception cơ sở cho các lỗi trong service."""
    pass


class VideoNotFoundError(ServiceError):
    """Lỗi khi video không tìm thấy hoặc không thể truy cập."""
    pass


class ConversionError(ServiceError):
    """Lỗi trong quá trình chuyển đổi hoặc tải video."""
    pass


class SetupError(ServiceError):
    """Lỗi liên quan đến cài đặt môi trường (ví dụ: thiếu ffmpeg)."""
    pass


async def service_error_handler(request: Request, exc: ServiceError):
    status_code = 500
    error_code = "INTERNAL_SERVER_ERROR"
    message = "An internal server error occurred."

    if isinstance(exc, VideoNotFoundError):
        status_code = 404
        error_code = "VIDEO_NOT_FOUND"
        message = str(exc)
    elif isinstance(exc, ConversionError):
        status_code = 500
        error_code = "VIDEO_CONVERSION_FAILED"
        message = str(exc)
    elif isinstance(exc, SetupError):
        status_code = 500
        error_code = "SERVER_CONFIGURATION_ERROR"
        message = str(exc)

    error_response = ErrorResponse(code=error_code, message=message)
    response_content = ModelResponse(success=False, error=error_response).model_dump()

    return JSONResponse(
        status_code=status_code,
        content=response_content,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Bắt lỗi RequestValidationError và định dạng lại theo cấu trúc ModelResponse.
    """
    details = [
        ErrorDetail(
            loc=[str(loc) for loc in err.get("loc", [])],
            msg=err.get("msg"),
            type=err.get("type")
        ) for err in exc.errors()
    ]

    error_response = ErrorResponse(
        code="VALIDATION_ERROR",
        message="Input validation failed.",
        details=details
    )
    response_content = ModelResponse(success=False, error=error_response).model_dump()

    return JSONResponse(
        status_code=422,
        content=response_content,
    )


async def generic_exception_handler(request: Request, exc: Exception):
    error_response = ErrorResponse(
        code="UNEXPECTED_ERROR",
        message="An unexpected internal server error occurred."
    )
    response_content = ModelResponse(success=False, error=error_response).model_dump()

    return JSONResponse(
        status_code=500,
        content=response_content
    )