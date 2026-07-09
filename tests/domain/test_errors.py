from app.domain.errors import ServiceInvalidStatusCodeError


def test_service_invalid_status_code_error_message() -> None:
    error = ServiceInvalidStatusCodeError(status=404, details="not found")
    status = 404
    assert str(error) == "External service returned invalid status: 404"
    assert error.status == status
    assert error.details == "not found"
