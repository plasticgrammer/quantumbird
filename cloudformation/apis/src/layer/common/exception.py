
class ApplicationException(Exception):
    """
    アプリケーション例外クラス
    """
    def __init__(self, status_code, message):
        self.status_code = status_code
        super().__init__(message)