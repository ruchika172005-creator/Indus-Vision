from abc import ABC, abstractmethod
from typing import Dict, Any, List

class VisionLanguageProvider(ABC):
    """
    Abstract interface for Vision-Language Model providers.
    Allows swappable multimodal backends (Google Gemini, Local VLM, Ollama, OpenAI Vision, etc.)
    """

    @abstractmethod
    async def generate_explanation(
        self,
        image_path: str,
        defects: List[Dict[str, Any]],
        product_category: str,
        detection_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Takes the product image and computer vision detection telemetry,
        and returns a structured JSON explanation.
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the provider is properly authenticated and ready."""
        pass
