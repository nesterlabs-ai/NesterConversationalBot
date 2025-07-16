"""Configuration for the Voice RAG Assistant."""

import os
import re
from pathlib import Path
from typing import Dict, Any, Union

import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
def _substitute_env_vars(config: Union[Dict, list, str]) -> Union[Dict, list, str]:
    """Recursively substitute environment variables in configuration.
    
    Args:
        config: Configuration object (dict, list, or string)
        
    Returns:
        Configuration with environment variables substituted
    """
    if isinstance(config, dict):
        return {key: _substitute_env_vars(value) for key, value in config.items()}
    elif isinstance(config, list):
        return [_substitute_env_vars(item) for item in config]
    elif isinstance(config, str):
        # Pattern to match ${VAR_NAME} or ${VAR_NAME:default_value}
        pattern = r'\$\{([^}]+)\}'
        matches = re.findall(pattern, config)

        result = config
        for match in matches:
            var_name = match
            default_value = ""

            # Check if there's a default value specified
            if ':' in match:
                var_name, default_value = match.split(':', 1)

            # Get environment variable value
            env_value = os.getenv(var_name, default_value)

            # Replace the placeholder with the actual value
            result = result.replace(f'${{{match}}}', env_value)

        return result
    else:
        return config


def load_config_from_yaml(config_file: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    Args:
        config_file: Path to the YAML configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the YAML file is malformed
    """
    config_path = Path(__file__).parent / config_file

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Substitute environment variables
    config = _substitute_env_vars(config)

    return config


def get_assistant_config() -> Dict[str, Any]:
    """Get configuration for the Voice Assistant.
    
    Returns:
        Configuration dictionary for all services
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the YAML file is malformed
        ValueError: If required environment variables are missing
    """
    config = load_config_from_yaml()

    # Validate that required API keys are set
    required_keys = [
        ("tts.config.api_key", config.get("tts", {}).get("config", {}).get("api_key")),
        ("tts.config.voice_id", config.get("tts", {}).get("config", {}).get("voice_id")),
        ("conversation.llm.api_key", config.get("conversation", {}).get("llm", {}).get("api_key"))
    ]

    missing_keys = []
    for key_path, value in required_keys:
        if not value or value.startswith("${"):
            missing_keys.append(key_path)

    if missing_keys:
        raise ValueError(
            f"Missing required environment variables for: {', '.join(missing_keys)}. "
            f"Please check your .env file and config.yaml"
        )

    return config


# Default configuration - can be imported directly if needed
# Note: This will raise exceptions if configuration is invalid
try:
    DEFAULT_CONFIG = get_assistant_config()
except (FileNotFoundError, yaml.YAMLError, ValueError) as e:
    print(f"Warning: Could not load default configuration: {e}")
    DEFAULT_CONFIG = None
