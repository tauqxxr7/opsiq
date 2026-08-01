import json
import logging
import re

import google.generativeai as genai

from core.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "gu": "Gujarati",
    "bn": "Bengali",
    "en": "English",
}


class TranslationService:
    def __init__(self):
        self.model = None
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")

    def detect_and_translate_to_english(self, text: str) -> dict:
        hint = re.match(r"^\[target_language=(hi|mr|ta|te|gu|bn|en)\]\s*", text)
        requested_language = hint.group(1) if hint else None
        source_text = text[hint.end():] if hint else text
        if not source_text.strip() or self.model is None:
            return {
                "translated": source_text,
                "lang": "en",
                "lang_name": "English",
                "is_english": True,
            }

        prompt = f"""Detect the language of this text and translate it to English.

Text: {source_text}

Respond in this exact JSON format:
{{
  "detected_language": "language code (en/hi/mr/ta/te/gu/bn)",
  "detected_language_name": "language name",
  "english_translation": "English translation",
  "is_english": true or false
}}

If already English, set is_english to true and repeat the original text as translation."""
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(
                response.text.strip().replace("```json", "").replace("```", "")
            )
            language = requested_language or result.get("detected_language", "en")
            if language not in SUPPORTED_LANGUAGES:
                language = "en"
            return {
                "translated": result.get("english_translation", source_text),
                "lang": language,
                "lang_name": SUPPORTED_LANGUAGES[language],
                "is_english": language == "en" and bool(result.get("is_english", True)),
            }
        except Exception as error:
            logger.warning("Translation failed: %s", error)
            return {
                "translated": source_text,
                "lang": "en",
                "lang_name": "English",
                "is_english": True,
            }

    def translate_response_to_language(self, text: str, target_lang: str) -> str:
        if target_lang == "en" or self.model is None:
            return text
        language_name = SUPPORTED_LANGUAGES.get(target_lang)
        if language_name is None:
            return text

        prompt = f"""Translate this industrial safety and maintenance response to {language_name}.

Keep all technical terms, equipment IDs (like P-201, V-101), standard references
(like OISD-118), citation markers, and numbers in English. Only translate descriptive text.

Text to translate:
{text}

Return only the translated text, no explanation."""
        try:
            return self.model.generate_content(prompt).text.strip()
        except Exception as error:
            logger.warning("Response translation failed: %s", error)
            return text
