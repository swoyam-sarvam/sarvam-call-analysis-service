import asyncio
import os
import httpx # type: ignore
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# OpenAI API configuration
SUBSCRIPTION_KEY = os.getenv("AZURE_OPENAI_API_KEY", "none")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "none")


def generate_system_prompt(config: Dict[str, str]) -> str:
    """Generate system prompt dynamically based on config"""
    prompt = """You are an AI assistant analyzing call transcripts for various flags based on the provided configuration.

Please analyze the transcript according to these specific criteria:

"""

    for flag_name, description in config.items():
        prompt += f"{flag_name}: {description}\n\n"

    prompt += """
Analyze the transcript provided and return a JSON response with the following format:
{
"""

    for flag_name in config.keys():
        prompt += f'    "{flag_name}": "yes" or "no",\n'

    prompt = prompt.rstrip(",\n") + "\n}"

    prompt += """

Rules for response:
- Return ONLY the JSON object, no additional text
- Use "yes" if the flag condition is met, "no" if it's not
- Be precise in your analysis based on the exact criteria provided
"""

    return prompt


async def analyze_transcript_with_config(
    transcript: str, config: Dict[str, str]
) -> Dict[str, str]:
    """
    Analyze a transcript against provided config flags using OpenAI API

    Args:
        transcript (str): The call transcript to analyze
        config (Dict[str, str]): Configuration dictionary with flag names as keys and descriptions as values

    Returns:
        Dict[str, str]: Dictionary with flag names as keys and "yes"/"no" as values
    """

    # Generate dynamic system prompt based on config
    system_prompt = generate_system_prompt(config)

    # Prepare user content
    user_content = f"Transcript: {transcript}"

    # Prepare messages for API call
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    headers = {
        "Authorization": f"Bearer {SUBSCRIPTION_KEY}",
        "Content-Type": "application/json",
    }

    data = {"model": "gpt-4o", "messages": messages, "temperature": 0}

    try:
        async with httpx.AsyncClient() as client:
            print(OPENAI_API_URL)
            response = await client.post(OPENAI_API_URL, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                api_response = result["choices"][0]["message"]["content"]

                # Extract JSON from response using regex
                json_result = extract_json_from_response(api_response)

                # Validate that all config keys are present in the result
                validated_result = validate_response(json_result, config)

                return validated_result

            else:
                print(f"Error in API call: {response.status_code}")
                # Return default "no" for all flags in case of API error
                return {flag: "no" for flag in config.keys()}

    except Exception as e:
        print(f"Exception in API call: {str(e)}")
        # Return default "no" for all flags in case of exception
        return {flag: "no" for flag in config.keys()}


def extract_json_from_response(response: str) -> Dict[str, str]:
    """
    Extract JSON object from OpenAI response using regex

    Args:
        response (str): Raw response from OpenAI API

    Returns:
        Dict[str, str]: Parsed JSON object
    """
    try:
        # Remove any markdown code blocks and extra whitespace
        cleaned_response = response.strip()

        # Remove markdown json blocks if present
        if cleaned_response.startswith("```"):
            # Find the JSON content between code blocks
            json_match = re.search(
                r"```(?:json)?\s*(\{.*?\})\s*```", cleaned_response, re.DOTALL
            )
            if json_match:
                cleaned_response = json_match.group(1)

        # Remove any leading/trailing backticks and "json" keyword
        cleaned_response = re.sub(r"^`*json\s*", "", cleaned_response)
        cleaned_response = re.sub(r"`*$", "", cleaned_response)

        # Try to find JSON object pattern
        json_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
        json_match = re.search(json_pattern, cleaned_response, re.DOTALL)

        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = cleaned_response

        # Parse the JSON
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from response: {e}")
        print(f"Response was: {response}")
        return {}
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return {}


def validate_response(
    json_result: Dict[str, str], config: Dict[str, str]
) -> Dict[str, str]:
    """
    Validate that the response contains all required flags and has valid values

    Args:
        json_result (Dict[str, str]): Parsed JSON result from API
        config (Dict[str, str]): Original config with expected flag names

    Returns:
        Dict[str, str]: Validated result with all config keys present
    """
    validated_result = {}

    for flag_name in config.keys():
        if flag_name in json_result:
            value = json_result[flag_name].lower()
            # Ensure value is either "yes" or "no"
            if value in ["yes", "no"]:
                validated_result[flag_name] = value
            else:
                # Default to "no" for invalid values
                validated_result[flag_name] = "no"
        else:
            # Default to "no" for missing flags
            validated_result[flag_name] = "no"

    return validated_result

