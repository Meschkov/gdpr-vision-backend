class AppConfig:
    def __init__(self,
                 header_key: str,
                 header_value: str,
                 ) -> None:
        self.AuthHeaderKey = header_key
        self.AuthHeaderValue = header_value
