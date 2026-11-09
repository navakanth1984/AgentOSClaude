"""
Direct Live Integration with AIKosh National Platform SDK (MeitY / IndiaAI)
Uses credentials from D:/navakanth001/.env
"""

from typing import Optional, Dict, Any, List
from .config import IndigenousConfig, default_config

try:
    import aikosh
    import aikosh.models
    import aikosh.datasets
except ImportError:
    aikosh = None

class AIKoshHub:
    def __init__(self, config: Optional[IndigenousConfig] = None):
        self.config = config or default_config
        self.access_key = self.config.aikosh_api_key
        if aikosh and self.access_key:
            try:
                aikosh.set_api_key(self.access_key)
            except Exception:
                pass

    def ping(self) -> Dict[str, Any]:
        """Test live connectivity to the AIKosh platform."""
        if not aikosh:
            return {"status": "error", "message": "aikosh package not installed"}
        return aikosh.ping()

    def list_models(self, page: int = 1, size: int = 20, keyword: Optional[str] = None) -> Dict[str, Any]:
        """Queries live sovereign models hosted on AIKosh."""
        if not aikosh or not self.access_key:
            return {"status": "error", "message": "AIKosh SDK or AIKOSH_API_KEY missing"}
        
        return aikosh.models.list_models(
            access_key=self.access_key,
            page=page,
            size=size,
            keyword=keyword
        )

    def get_model_metadata(self, model_id: str) -> Dict[str, Any]:
        """Retrieves technical specification, license, and parameter details for a specific model."""
        if not aikosh or not self.access_key:
            return {"status": "error", "message": "AIKosh SDK or AIKOSH_API_KEY missing"}
        return aikosh.models.get_model_metadata(access_key=self.access_key, model_id=model_id)

    def search_indic_models(self, query: str = "Indic") -> List[Dict[str, Any]]:
        """Convenience method to search specifically for Indic language/vision/speech models."""
        res = self.list_models(page=1, size=50, keyword=query)
        return res.get("data", [])
