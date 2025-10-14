from fastapi import HTTPException, status

class StudentException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class ValidationException(StudentException):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class StudentNotFoundError(StudentException):
    def __init__(self, student_id: str = None, id: int = None):
        if student_id:
            detail = f"Student with ID {student_id} not found"
        elif id:
            detail = f"Student with database ID {id} not found"
        else:
            detail = "Student not found"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class StudentAlreadyExistsError(StudentException):
    def __init__(self, student_id: str):
        detail = f"Student with ID {student_id} already exists"
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)

class BulkImportError(StudentException):
    def __init__(self, detail: str, errors: list = None):
        self.errors = errors or []
        super().__init__(detail=detail)
