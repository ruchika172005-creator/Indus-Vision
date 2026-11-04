import base64
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx

from app.genai.provider import VisionLanguageProvider
from app.genai.prompt_templates import SYSTEM_INSTRUCTION, build_defect_analysis_prompt
from app.genai.response_validator import ResponseValidator
from app.core.config import settings
from app.core.logging import logger

class GeminiVisionProvider(VisionLanguageProvider):
    """
    Google Gemini Multimodal Vision-Language Provider.
    Calls Google Generative Language REST API directly with base64 image encoding,
    structured JSON output enforcement, and zero heavy dependencies.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", settings.GEMINI_API_KEY)
        self.model_name = model_name or settings.GEMINI_MODEL or "gemini-1.5-flash"
        self.timeout = settings.GENAI_TIMEOUT_SECONDS

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    async def generate_explanation(
        self,
        image_path: str,
        defects: List[Dict[str, Any]],
        product_category: str,
        detection_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("Gemini API key is not configured.")

        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image for GenAI analysis not found at {image_path}")

        # Read image and encode as base64
        with open(path, "rb") as f:
            image_bytes = f.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        mime_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"

        prompt = build_defect_analysis_prompt(
            product_category=product_category,
            defects=defects,
            metadata=detection_metadata
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_b64
                            }
                        },
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Gemini API returned HTTP {response.status_code}: {response.text}")
                raise RuntimeError(f"Gemini API error ({response.status_code}): {response.text}")

            result = response.json()
            candidates = result.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned by Gemini model.")

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise ValueError("Empty content part from Gemini model.")

            raw_text = parts[0].get("text", "{}")
            validated = ResponseValidator.parse_and_validate(raw_text)
            validated["provider_used"] = f"Google Gemini ({self.model_name})"
            return validated
