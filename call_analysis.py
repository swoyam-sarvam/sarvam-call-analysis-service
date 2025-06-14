import asyncio
import os
import httpx  # type: ignore
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# OpenAI API configuration
OPENAI_URL = os.getenv("OPENAI_API_URL", "none")
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "none")

#Sarvam API configuration
SARVAM_URL = os.getenv("SARVAM_API_URL", "none")
SARVAM_API_KEY = os.getenv("SARVAM_SUBSCRIPTION_KEY", "none")


# LLAMA API configuration
LLAMA_URL = os.getenv("LLAMA_URL", "none")
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY", "none")


def generate_system_prompt(config: Dict[str, str]) -> str:
    """
    Generate an improved system prompt for the AI assistant to analyze call transcripts
    and provide answers as per the description in the config, not just "yes" or "no".
    """
    prompt = (
        "You are a highly capable AI assistant tasked with analyzing call transcripts. "
        "Your goal is to extract detailed, accurate, and contextually relevant information "
        "for each of the following criteria. For each flag, provide a direct answer as specified "
        "Instructions:\n"
        "- Carefully read the transcript and evaluate each flag based on its description.\n"
        "- For each flag, provide the answer in the format and detail requested in the description.\n"
        "- If the answer is not present or cannot be determined, respond with 'Not found' or an appropriate message as per the flag's requirement.\n"
        "- Return ONLY a valid JSON object as your response, with no extra commentary or formatting.\n"
        "- Be concise, accurate, and strictly follow the requirements for each flag.\n\n"
        "Criteria and expected answers:\n"
    )

    for flag_name, description in config.items():
        prompt += f"- {flag_name}: {description}\n"

    prompt += (
        "\nAfter analyzing the transcript, respond with a JSON object in the following format:\n"
        "{\n"
    )

    for flag_name, description in config.items():
        prompt += f'    "{flag_name}": <answer as per description>,\n'

    prompt = prompt.rstrip(",\n") + "\n}"

    prompt += (
        "\n\nExample:\n"
        "{\n"
    )
    for flag_name, description in config.items():
        prompt += f'    "{flag_name}": "<example answer as per description>",\n'
    prompt = prompt.rstrip(",\n") + "\n}\n"

    prompt += (
        "\nRemember:\n"
        "- Do NOT include any explanations, markdown, or extra text.\n"
        "- Only output the JSON object as specified above.\n"
    )

    return prompt


async def analyze_transcript_with_config_llama(
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
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLAMA_API_KEY}",
    }

    data = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": messages,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LLAMA_URL, headers=headers, json=data, timeout=30.0  # Add timeout
            )

            if response.status_code == 200:
                result = response.json()
                api_response = result["choices"][0]["message"]["content"]

                # Extract JSON from response using regex
                json_result = extract_json_from_response(api_response)

                return json_result

            else:
                print(f"Error in API call: {response.status_code}")
                print(f"Response text: {response.text}")
                # Return default "failed" for all flags in case of API error
                return {flag: "failed" for flag in config.keys()}

    except Exception as e:
        print(f"Exception in API call: {str(e)}")
        # Return default "failed" for all flags in case of exception
        return {flag: "failed" for flag in config.keys()}


async def analyze_transcript_with_config_gpt4o(
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
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {"model": "gpt-4o", "messages": messages, "temperature": 0}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENAI_URL, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                api_response = result["choices"][0]["message"]["content"]

                # Extract JSON from response using regex
                json_result = extract_json_from_response(api_response)

                return json_result

            else:
                print(f"Error in API call: {response.status_code}")
                # Return default "failed" for all flags in case of API error
                return {flag: "failed" for flag in config.keys()}

    except Exception as e:
        print(f"Exception in API call: {str(e)}")
        # Return default "failed" for all flags in case of exception
        return {flag: "failed" for flag in config.keys()}


async def analyze_transcript_with_config_sarvam(
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
        "api-subscription-key": SARVAM_API_KEY,  # Use correct subscription key
        "Content-Type": "application/json",
    }

    data = {"model": "sarvam-m", "messages": messages}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SARVAM_URL,
                headers=headers,
                json=data,
                timeout=30.0  # Add timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                api_response = result["choices"][0]["message"]["content"]

                # Extract JSON from response using regex
                json_result = extract_json_from_response(api_response)

                await asyncio.sleep(30)
                return json_result

            else:
                print(f"Error in API call: {response.status_code}")
                print(f"Response text: {response.text}")
                # Return default "failed" for all flags in case of API error
                return {flag: "failed" for flag in config.keys()}

    except Exception as e:
        print(f"Exception in API call: {str(e)}")
        # Return default "failed" for all flags in case of exception
        return {flag: "failed" for flag in config.keys()}


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


async def analyze_transcript_with_config(
    transcript: str, config: Dict[str, str], model: str
) -> Optional[Dict[str, str]]:
    """
    Analyze transcript with the specified model.

    Args:
        transcript (str): The transcript to analyze.
        config (Dict[str, str]): The analysis configuration.
        model (str): The model to use for analysis.

    Returns:
        Optional[Dict[str, str]]: Analysis result or None if model is unknown.
    """
    if model == "llama":
        return await analyze_transcript_with_config_llama(transcript, config)
    elif model == "gpt4o":
        return await analyze_transcript_with_config_gpt4o(transcript, config)
    elif model == "sarvam-m":
        return await analyze_transcript_with_config_sarvam(transcript, config)
    else:
        # Handle unknown model
        print(f"Unknown model: {model}")
        return None
