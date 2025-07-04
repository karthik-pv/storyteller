import random
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class CategoriesService:
    def __init__(self):
        """Initialize categories service with predefined categories"""
        self.categories = {
            "Adventure": [
                "Treasure_Hunt",
                "Space_Exploration",
                "Jungle_Safari",
                "Underwater_World",
            ],
            "Sports": [
                "Football",
                "Basketball",
                "Martial_Arts",
                "Gymnastics",
                "Racing",
            ],
            "Safety": [
                "Stranger_Danger",
                "Fire_Safety",
                "Internet_Safety",
                "Road_Safety",
            ],
            "Magic": [
                "Wizards",
                "Witches",
                "Potions",
                "Magical_Creatures",
                "Enchanted_Forests",
            ],
            "Fairytale": [
                "Royalty",
                "Dragons",
                "Castles",
                "Villains",
                "Magical_Spells",
            ],
            "Education": ["Science", "History", "Cooking", "Reading", "Art", "Music"],
            "Friendship": [
                "New_Friends",
                "Helping_Others",
                "Teamwork",
                "Overcoming_Challenges",
                "Loyalty",
            ],
            "Family": ["Family_Adventures", "Holidays", "Sibling_Bonds", "Parenthood"],
            "Mystery": [
                "Detective_Stories",
                "Secret_Codes",
                "Hidden_Objects",
                "Puzzles",
            ],
            "Holidays_&_Celebrations": [
                "Birthdays",
                "Christmas",
                "Halloween",
                "Easter",
                "Cultural_Festivals",
            ],
            "Nature_&_Environment": [
                "Wildlife_Conservation",
                "Gardening",
                "Recycling",
                "Weather",
                "Ocean_Life",
            ],
            "Special_Needs_Awareness": [
                "Understanding_Differences",
                "Inclusivity",
                "Overcoming_Obstacles",
                "Empathy",
            ],
            "Careers_&_Aspirations": [
                "Future_Jobs",
                "Dream_Big",
                "Role_Models",
                "Achieving_Goals",
                "Passion_Projects",
            ],
            "Travel_&_Exploration": [
                "World_Cultures",
                "Famous_Landmarks",
                "Language_Learning",
                "Expedition",
                "Time_Travel",
            ],
        }
        logger.info(
            f"Categories service initialized with {len(self.categories)} categories"
        )

    def get_all_categories(self) -> Dict[str, List[str]]:
        """
        Get all available categories and their subcategories

        Returns:
            Dictionary of categories and subcategories
        """
        return self.categories.copy()

    def get_category_list(self) -> List[str]:
        """
        Get list of all category names

        Returns:
            List of category names
        """
        return list(self.categories.keys())

    def get_subcategories(self, category: str) -> List[str]:
        """
        Get subcategories for a specific category

        Args:
            category: The category name

        Returns:
            List of subcategories for the given category
        """
        return self.categories.get(category, [])

    def get_random_category_and_subcategory(self) -> Tuple[str, str]:
        """
        Get a random category and subcategory combination

        Returns:
            Tuple of (category, subcategory)
        """
        # Select random category
        category = random.choice(self.get_category_list())

        # Select random subcategory from the chosen category
        subcategories = self.get_subcategories(category)
        subcategory = random.choice(subcategories)

        logger.info(f"Random selection: {category} -> {subcategory}")
        return category, subcategory

    def validate_category_subcategory(self, category: str, subcategory: str) -> bool:
        """
        Validate if a category and subcategory combination is valid

        Args:
            category: The category name
            subcategory: The subcategory name

        Returns:
            True if valid, False otherwise
        """
        if category not in self.categories:
            logger.error(f"Invalid category: {category}")
            return False

        if subcategory not in self.categories[category]:
            logger.error(
                f"Invalid subcategory '{subcategory}' for category '{category}'"
            )
            return False

        return True

    def format_category_display(self, category: str) -> str:
        """
        Format category name for display (replace underscores with spaces)

        Args:
            category: The category name

        Returns:
            Formatted category name
        """
        return category.replace("_", " ")

    def format_subcategory_display(self, subcategory: str) -> str:
        """
        Format subcategory name for display (replace underscores with spaces)

        Args:
            subcategory: The subcategory name

        Returns:
            Formatted subcategory name
        """
        return subcategory.replace("_", " ")


# Global instance for easy access
categories_service = CategoriesService()
