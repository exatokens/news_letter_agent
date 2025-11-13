"""
Prompt loader for news gatherer agent using YAML
"""
import yaml
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class NewsGathererPrompts:
    """Loads and manages prompts from YAML file"""

    def __init__(self, yaml_path: str = "prompts/news_gatherer.yaml"):
        """
        Initialize prompt loader

        Args:
            yaml_path: Path to the YAML prompt file
        """
        self.yaml_path = Path(yaml_path)
        self._prompts: Dict[str, Any] = {}
        self._load_prompts()
        logger.info(f"Loaded prompts from: {self.yaml_path}")

    def _load_prompts(self):
        """Load prompts from YAML file"""
        try:
            with open(self.yaml_path, 'r', encoding='utf-8') as f:
                self._prompts = yaml.safe_load(f)

            # Log metadata
            metadata = self._prompts.get('metadata', {})
            logger.info(f"Prompt version: {metadata.get('version')}")
            logger.info(f"Last updated: {metadata.get('last_updated')}")

        except FileNotFoundError:
            logger.error(f"Prompt file not found: {self.yaml_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            raise

    def get_system_prompt(self, **kwargs) -> str:
        """
        Get system prompt with variable substitution

        Args:
            **kwargs: Variables to inject (e.g., max_articles, top_articles)

        Returns:
            Formatted system prompt
        """
        prompt_template = self._prompts.get('system_prompt', '')

        # Merge default variables with provided kwargs
        variables = self._prompts.get('variables', {})
        variables.update(kwargs)

        try:
            return prompt_template.format(**variables)
        except KeyError as e:
            logger.error(f"Missing variable in system prompt: {e}")
            raise ValueError(f"Missing required variable: {e}")

    def get_user_prompt(self, user_request: str, **kwargs) -> str:
        """
        Get user prompt with variable substitution

        Args:
            user_request: The user's news request
            **kwargs: Additional variables to inject

        Returns:
            Formatted user prompt
        """
        prompt_template = self._prompts.get('user_prompt', '')

        # Merge default variables with provided kwargs
        variables = self._prompts.get('variables', {})
        variables.update(kwargs)
        variables['user_request'] = user_request

        try:
            return prompt_template.format(**variables)
        except KeyError as e:
            logger.error(f"Missing variable in user prompt: {e}")
            raise ValueError(f"Missing required variable: {e}")

    def get_metadata(self) -> Dict[str, Any]:
        """Get prompt metadata"""
        return self._prompts.get('metadata', {})

    def reload(self):
        """Reload prompts from file"""
        self._load_prompts()
        logger.info("Prompts reloaded")

