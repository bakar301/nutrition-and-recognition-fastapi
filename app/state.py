class AnalyzerState:
    def __init__(self):
        self.path = ""
        self.user_id: str = ""
        self.analysis_result = None
        
    def get_user_id(self) -> str:
        return self.user_id
    
    def set_user_id(self, user_id: str):
        self.user_id = user_id
    
    def get_path(self) -> str:
        return self.path    
    
    def set_path(self, path: str):
        self.path = path
    
    def set_analysis_result(self, result: dict):
        self.analysis_result = result
        
    def get_analysis_result(self) -> dict:
        return self.analysis_result if self.analysis_result else {}
    
