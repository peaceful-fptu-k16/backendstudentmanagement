import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional
import json

from app.core.config import settings


class StudentManagementLogger:
    def __init__(self):
        self.base_log_dir = "logs"
        self.current_date = None
        self.current_log_dir = None
        self.loggers = {}
        self._update_log_directory()
        
    def _update_log_directory(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.current_date != today:
            self.current_date = today
            self.current_log_dir = os.path.join(self.base_log_dir, today)
            self.ensure_log_directory()
            if self.loggers:
                self.loggers.clear()
        
    def ensure_log_directory(self):
        os.makedirs(self.current_log_dir, exist_ok=True)
    
    def get_logger(self, name: str, level: str = "INFO") -> logging.Logger:
        self._update_log_directory()
        
        logger_key = f"{self.current_date}_{name}"
        if logger_key in self.loggers:
            return self.loggers[logger_key]
        
        logger = logging.getLogger(f"{name}_{self.current_date}")
        logger.setLevel(getattr(logging, level.upper()))
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=os.path.join(self.current_log_dir, f"{name}.log"),
            when='H',
            interval=1,
            backupCount=24,
            encoding='utf-8'
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        error_handler = logging.handlers.TimedRotatingFileHandler(
            filename=os.path.join(self.current_log_dir, f"{name}_errors.log"),
            when='H',
            interval=1,
            backupCount=24,
            encoding='utf-8'
        )
        error_handler.setFormatter(detailed_formatter)
        error_handler.setLevel(logging.ERROR)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)
        
        self.loggers[logger_key] = logger
        
        return logger
    
    def get_api_logger(self) -> logging.Logger:
        return self.get_logger("api", "INFO")
    
    def get_database_logger(self) -> logging.Logger:
        return self.get_logger("database", "INFO")
    
    def get_service_logger(self) -> logging.Logger:
        return self.get_logger("service", "INFO")
    
    def get_crawler_logger(self) -> logging.Logger:
        return self.get_logger("crawler", "INFO")
    
    def get_export_logger(self) -> logging.Logger:
        return self.get_logger("export", "INFO")
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        import shutil
        from datetime import timedelta
        
        try:
            if not os.path.exists(self.base_log_dir):
                return
                
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for folder_name in os.listdir(self.base_log_dir):
                folder_path = os.path.join(self.base_log_dir, folder_name)
                
                if os.path.isdir(folder_path):
                    try:
                        folder_date = datetime.strptime(folder_name, "%Y-%m-%d")
                        
                        if folder_date < cutoff_date:
                            shutil.rmtree(folder_path)
                            print(f"Cleaned up old log folder: {folder_name}")
                            
                    except ValueError:
                        continue
                        
        except Exception as e:
            print(f"Error during log cleanup: {e}")
    
    def get_current_log_folder(self) -> str:
        self._update_log_directory()
        return self.current_log_dir


class StructuredLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_api_request(self, method: str, path: str, remote_addr: str, user_agent: Optional[str] = None):
        log_data = {
            "event": "api_request",
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "path": path,
            "remote_addr": remote_addr,
            "user_agent": user_agent
        }
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_api_response(self, method: str, path: str, status_code: int, duration: float, response_size: Optional[int] = None):
        log_data = {
            "event": "api_response",
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "response_size": response_size
        }
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_database_query(self, operation: str, table: str, duration: Optional[float] = None, record_count: Optional[int] = None):
        log_data = {
            "event": "database_operation",
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "table": table,
            "duration_ms": round(duration * 1000, 2) if duration else None,
            "record_count": record_count
        }
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_student_operation(self, operation: str, student_id: Optional[str] = None, details: Optional[dict] = None):
        log_data = {
            "event": "student_operation",
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "student_id": student_id,
            "details": details or {}
        }
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_data_import(self, file_name: str, file_type: str, processed: int, successful: int, failed: int, errors: list):
        log_data = {
            "event": "data_import",
            "timestamp": datetime.now().isoformat(),
            "file_name": file_name,
            "file_type": file_type,
            "processed": processed,
            "successful": successful,
            "failed": failed,
            "errors": errors[:10]
        }
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_data_export(self, format: str, record_count: int, file_size: Optional[int] = None, duration: Optional[float] = None):
        log_data = {
            "event": "data_export",
            "timestamp": datetime.now().isoformat(),
            "format": format,
            "record_count": record_count,
            "file_size": file_size,
            "duration_ms": round(duration * 1000, 2) if duration else None
        }
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_crawler_operation(self, url: str, operation: str, success: bool, records_found: Optional[int] = None, error: Optional[str] = None):
        log_data = {
            "event": "crawler_operation",
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "operation": operation,
            "success": success,
            "records_found": records_found,
            "error": error
        }
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_error(self, error_type: str, error_message: str, stack_trace: Optional[str] = None, context: Optional[dict] = None):
        log_data = {
            "event": "application_error",
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "context": context or {}
        }
        self.logger.error(json.dumps(log_data, ensure_ascii=False))


logger_manager = StudentManagementLogger()

def get_api_logger() -> logging.Logger:
    return logger_manager.get_api_logger()

def get_database_logger() -> logging.Logger:
    return logger_manager.get_database_logger()

def get_service_logger() -> logging.Logger:
    return logger_manager.get_service_logger()

def get_crawler_logger() -> logging.Logger:
    return logger_manager.get_crawler_logger()

def get_export_logger() -> logging.Logger:
    return logger_manager.get_export_logger()

def get_structured_logger(logger_name: str) -> StructuredLogger:
    logger = logger_manager.get_logger(logger_name)
    return StructuredLogger(logger)