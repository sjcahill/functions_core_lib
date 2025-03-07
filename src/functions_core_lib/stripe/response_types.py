from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CreateCustomerApiResponse:
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None
    status_code: int = 200

    def to_response(self) -> tuple[dict[str, Any], int]:
        """Convert to response tuple for Cloud Functions"""
        response_data = {"success": self.success, "message": self.message}

        if self.data is not None:
            response_data["data"] = self.data

        if self.error_code is not None:
            response_data["error_code"] = self.error_code

        return response_data, self.status_code
