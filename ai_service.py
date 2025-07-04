import os
import json
import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        """Initialize AI service with Gemini API"""
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            logger.error("GEMINI_API_KEY environment variable is not set!")
            raise ValueError("GEMINI_API_KEY environment variable is required")

        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("Gemini AI service initialized successfully")

    def get_base_story_prompt(
        self, category: str, subcategory: str, num_slides: int
    ) -> str:
        """
        Generate base prompt for story generation

        Args:
            category: The main story category
            subcategory: The specific subcategory
            num_slides: Number of slides/scenes in the story

        Returns:
            Formatted base prompt string
        """
        base_prompt = f"""
You are an expert children's story writer. Create an engaging, age-appropriate story for children aged 5-12 years.

STORY REQUIREMENTS:
- Category: {category}
- Subcategory: {subcategory}
- Number of slides/scenes: {num_slides}
- Each slide should have 2-3 sentences of story text
- Story should be educational, fun, and inspiring
- Use simple language appropriate for children
- Include positive messages and life lessons
- Make it interactive and engaging

CRITICAL IMAGE REQUIREMENTS:
- The user will upload an avatar image that represents the main character
- ALL image prompts MUST include the main character from the uploaded avatar
- The main character should be consistently present and recognizable in every scene
- Describe the character's actions, expressions, and interactions in each scene
- Ensure character consistency across all slides

IMPORTANT: Your response must be in valid JSON format with the following structure:
{{
    "story_title": "Title of the story",
    "category": "{category}",
    "subcategory": "{subcategory}",
    "slides": [
        {{
            "slide_number": 1,
            "story_text": "The story text for this slide (2-3 sentences)",
            "image_prompt": "Detailed image generation prompt featuring the main character from the uploaded avatar. Describe the character's appearance, actions, expressions, setting, and interactions. Style: cartoon/illustration suitable for children. The main character should be the focus of the scene."
        }},
        {{
            "slide_number": 2,
            "story_text": "The story text for this slide (2-3 sentences)",
            "image_prompt": "Detailed image generation prompt featuring the same main character from the uploaded avatar in a new scene"
        }}
    ]
}}

Make sure EVERY image prompt:
- Features the main character prominently
- Describes the character's specific actions and expressions
- Maintains character consistency throughout the story
- Includes detailed scene descriptions (setting, background, other elements)
- Specifies cartoon/illustration art style suitable for children
- Creates engaging, child-friendly visuals

The main character from the uploaded avatar should be the hero/protagonist of the story and appear in every single image.

Create a complete story with exactly {num_slides} slides.
"""
        return base_prompt

    def generate_story(
        self, category: str, subcategory: str, num_slides: int
    ) -> Dict[str, Any]:
        """
        Generate a complete story using Gemini API

        Args:
            category: Story category
            subcategory: Story subcategory
            num_slides: Number of slides

        Returns:
            Dictionary containing story data and the base prompt used
        """
        try:
            logger.info(
                f"Generating story for {category}/{subcategory} with {num_slides} slides"
            )

            prompt = self.get_base_story_prompt(category, subcategory, num_slides)

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean up response text (remove markdown formatting if present)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            # Parse JSON response
            story_data = json.loads(response_text)

            # Validate response structure
            if not self._validate_story_response(story_data, num_slides):
                raise ValueError("Invalid story response structure")

            # Add the base prompt to the response
            story_data["base_prompt"] = prompt

            logger.info(
                f"Story generated successfully: {story_data.get('story_title', 'Untitled')}"
            )
            return story_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from AI service: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            raise

    def _validate_story_response(
        self, story_data: Dict[str, Any], expected_slides: int
    ) -> bool:
        """
        Validate the structure of the story response

        Args:
            story_data: The parsed story data
            expected_slides: Expected number of slides

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["story_title", "category", "subcategory", "slides"]

        # Check required top-level fields
        for field in required_fields:
            if field not in story_data:
                logger.error(f"Missing required field: {field}")
                return False

        # Check slides structure
        slides = story_data.get("slides", [])
        if len(slides) != expected_slides:
            logger.error(f"Expected {expected_slides} slides, got {len(slides)}")
            return False

        # Check each slide structure
        for i, slide in enumerate(slides):
            required_slide_fields = ["slide_number", "story_text", "image_prompt"]
            for field in required_slide_fields:
                if field not in slide:
                    logger.error(f"Missing field '{field}' in slide {i+1}")
                    return False

            if (
                not isinstance(slide["story_text"], str)
                or not slide["story_text"].strip()
            ):
                logger.error(f"Invalid story_text in slide {i+1}")
                return False

            if (
                not isinstance(slide["image_prompt"], str)
                or not slide["image_prompt"].strip()
            ):
                logger.error(f"Invalid image_prompt in slide {i+1}")
                return False

        return True


# Alternative implementation for OpenAI (for future migration)
class OpenAIService:
    def __init__(self):
        """Initialize OpenAI service (for future use)"""
        # This will be implemented when migrating to OpenAI
        self.api_key = os.getenv("OPENAI_API_KEY")
        logger.info("OpenAI service initialized (not implemented yet)")

    def generate_story(
        self, category: str, subcategory: str, num_slides: int
    ) -> Dict[str, Any]:
        """
        Generate story using OpenAI API (placeholder for future implementation)
        """
        raise NotImplementedError("OpenAI service not implemented yet")


# Factory function to get the appropriate AI service
def get_ai_service(service_type: str = "gemini") -> AIService:
    """
    Factory function to get AI service instance

    Args:
        service_type: Type of AI service ("gemini" or "openai")

    Returns:
        AI service instance
    """
    if service_type.lower() == "gemini":
        return AIService()
    elif service_type.lower() == "openai":
        return OpenAIService()
    else:
        raise ValueError(f"Unsupported AI service type: {service_type}")
