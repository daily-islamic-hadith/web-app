import json
import logging
import os
from openai import OpenAI
from openai.types.shared_params.response_format_json_schema import JSONSchema
from openai.types.shared_params import ResponseFormatJSONSchema

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY','YOUR_API_KEY')
)


def fetch_hadith_explanation(hadith_txt):
    try:
        if hadith_txt is None or hadith_txt.strip() == '':
            return None
        msg = '\n تفسير او شرح الحديث \n ' + hadith_txt
        ai_response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": msg
                }

            ],
            model="gpt-4o-mini",
            response_format=ai_response_format
        )
        if not ai_response or not ai_response.choices:
            return None
        return json.loads(ai_response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Failed to fetch new explanation", e)
        return None


ai_response_format = ResponseFormatJSONSchema(
    json_schema=JSONSchema(
        name="language_keys",
        strict=True,
        schema={
            "type": "object",
            "required": [
                "en",
                "ar"
            ],
            "properties": {
                "ar": {
                    "type": "string",
                    "description": "The value for the Arabic language key."
                },
                "en": {
                    "type": "string",
                    "description": "The value for the English language key."
                }
            },
            "additionalProperties": False
        }
    ),
    type="json_schema"
)
