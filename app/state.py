class AnalyzerState:
    def __init__(self):
        self.path = ""
        self.user_id: str = ""
        
    def get_user_id(self) -> str:
        return self.user_id
    
    def set_user_id(self, user_id: str):
        self.user_id = user_id
    
    def get_path(self) -> str:
        return self.path    
    
    def set_path(self, path: str):
        self.path = path
    
