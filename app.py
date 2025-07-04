import os
import base64
import shutil
import logging
import json
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from PIL import Image
from io import BytesIO
import uuid
from dotenv import load_dotenv

# Import our new services
from ai_service import get_ai_service
from categories_service import categories_service

load_dotenv()

app = Flask(__name__)

# Configure logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate OpenAI API key on startup
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY environment variable is not set!")
    raise ValueError("OPENAI_API_KEY environment variable is required")

logger.info("OpenAI API key found, initializing client...")
client = OpenAI(api_key=api_key)

# Initialize AI service for story generation
try:
    ai_service = get_ai_service("gemini")
    logger.info("AI service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AI service: {str(e)}")
    ai_service = None

# Test directories on startup
try:
    os.makedirs("static", exist_ok=True)
    os.makedirs("static/avatars", exist_ok=True)
    logger.info("Static directories created successfully")
except Exception as e:
    logger.error(f"Failed to create static directories: {str(e)}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health_check():
    """Health check endpoint for Render"""
    try:
        # Check if OpenAI client is working
        api_key_status = "OK" if client.api_key else "MISSING"

        # Check AI service status
        ai_service_status = "OK" if ai_service else "MISSING"

        # Check if static directories exist
        static_dir_exists = os.path.exists("static")
        avatars_dir_exists = os.path.exists("static/avatars")

        return jsonify(
            {
                "status": "healthy",
                "api_key": api_key_status,
                "ai_service": ai_service_status,
                "static_dir": static_dir_exists,
                "avatars_dir": avatars_dir_exists,
            }
        )
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Get all available story categories and subcategories"""
    try:
        categories = categories_service.get_all_categories()
        return jsonify({"success": True, "categories": categories})
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-story", methods=["POST"])
def generate_story():
    """Generate a story based on category, subcategory, and number of slides"""
    try:
        if not ai_service:
            return jsonify({"error": "AI service not available"}), 500

        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Get parameters
        category = data.get("category")
        subcategory = data.get("subcategory")
        num_slides = data.get("num_slides", 5)
        use_random = data.get("use_random", False)

        # Validate number of slides
        if not isinstance(num_slides, int) or num_slides < 3 or num_slides > 10:
            return jsonify({"error": "Number of slides must be between 3 and 10"}), 400

        # Handle random selection
        if use_random:
            category, subcategory = (
                categories_service.get_random_category_and_subcategory()
            )
            logger.info(f"Random selection: {category} -> {subcategory}")
        else:
            # Validate provided category and subcategory
            if not category or not subcategory:
                return jsonify({"error": "Category and subcategory are required"}), 400

            if not categories_service.validate_category_subcategory(
                category, subcategory
            ):
                return jsonify({"error": "Invalid category or subcategory"}), 400

        # Generate story
        story_data = ai_service.generate_story(category, subcategory, num_slides)

        logger.info(
            f"Story generated successfully: {story_data.get('story_title', 'Untitled')}"
        )

        return jsonify({"success": True, "story": story_data})

    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-story-session", methods=["POST"])
def generate_story_session():
    """Initialize a story session with avatar and story data"""
    try:
        # Get uploaded avatar
        avatar_file = request.files.get("avatar")
        if not avatar_file:
            logger.error("No avatar file uploaded")
            return jsonify({"error": "No avatar file uploaded"}), 400

        logger.info(f"Avatar file received: {avatar_file.filename}")

        # Get story data from form
        story_data_json = request.form.get("story_data")
        if not story_data_json:
            return jsonify({"error": "No story data provided"}), 400

        try:
            story_data = json.loads(story_data_json)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid story data format"}), 400

        # Create unique session directory
        session_id = str(uuid.uuid4())
        output_dir = f"static/avatars/{session_id}"

        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created session directory: {output_dir}")
        except Exception as dir_error:
            logger.error(f"Failed to create session directory: {str(dir_error)}")
            return jsonify({"error": "Failed to create session directory"}), 500

        # Store avatar
        avatar_path = os.path.join(output_dir, "avatar.jpg")
        try:
            avatar_file.save(avatar_path)
            logger.info(f"Avatar saved to: {avatar_path}")

            # Verify the file was saved correctly
            if os.path.exists(avatar_path):
                file_size = os.path.getsize(avatar_path)
                logger.info(f"Avatar file saved successfully, size: {file_size} bytes")
            else:
                logger.error("Avatar file was not saved properly")
                return jsonify({"error": "Failed to save avatar file"}), 500

        except Exception as save_error:
            logger.error(f"Failed to save avatar: {str(save_error)}")
            return jsonify({"error": "Failed to save avatar file"}), 500

        # Store story data as JSON file
        story_path = os.path.join(output_dir, "story.json")
        try:
            with open(story_path, "w") as f:
                json.dump(story_data, f, indent=2)
            logger.info(f"Story data saved to: {story_path}")
        except Exception as story_save_error:
            logger.error(f"Failed to save story data: {str(story_save_error)}")
            return jsonify({"error": "Failed to save story data"}), 500

        logger.info("Story session initialized successfully")
        return jsonify(
            {
                "session_id": session_id,
                "story": story_data,
                "total_slides": len(story_data.get("slides", [])),
            }
        )

    except Exception as e:
        logger.error(f"Error in generate_story_session: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


@app.route(
    "/api/generate-story-image/<session_id>/<int:slide_number>", methods=["POST"]
)
def generate_story_image(session_id, slide_number):
    """Generate image for a specific story slide"""
    try:
        logger.info(f"Generating image for session {session_id}, slide {slide_number}")

        # Get image prompt from request
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        image_prompt = data.get("image_prompt")
        story_text = data.get("story_text", "")

        if not image_prompt:
            return jsonify({"error": "No image prompt provided"}), 400

        # Check if avatar exists
        avatar_dir = f"static/avatars/{session_id}"
        avatar_path = os.path.join(avatar_dir, "avatar.jpg")

        if not os.path.exists(avatar_path):
            logger.error(f"Avatar not found at path: {avatar_path}")
            return jsonify({"error": "Avatar not found"}), 400

        # Enhance the image prompt for better character consistency
        enhanced_prompt = f"""
Transform the uploaded character/avatar into this scene: {image_prompt}

IMPORTANT INSTRUCTIONS:
- Use the uploaded avatar as the main character in this scene
- Maintain the character's distinctive features, clothing, and appearance
- The character should be clearly recognizable and prominent in the image
- Keep the character's proportions and style consistent
- Make sure the character fits naturally into the scene described
- Style: Child-friendly cartoon/illustration
- The character should be the hero/protagonist of this scene

Scene context: {story_text}
"""

        logger.info(
            f"Generating image for slide {slide_number} with enhanced prompt: {enhanced_prompt[:100]}..."
        )

        # Always use OpenAI for image generation
        with open(avatar_path, "rb") as avatar_file_obj:
            logger.info("Avatar file opened successfully, calling OpenAI API...")

            result = client.images.edit(
                model="dall-e-2",
                image=avatar_file_obj,
                prompt=enhanced_prompt,
                size="1024x1024",
                n=1,
            )

            image_url = result.data[0].url

            # Download the image and convert to base64
            import requests

            response = requests.get(image_url)
            if response.status_code == 200:
                import base64

                image_base64 = base64.b64encode(response.content).decode("utf-8")
                logger.info(f"Generated image for slide {slide_number} successfully")

                return jsonify(
                    {
                        "success": True,
                        "image_base64": image_base64,
                        "filename": f"story_slide_{slide_number}.jpg",
                        "slide_number": slide_number,
                        "story_text": story_text,
                        "image_prompt": enhanced_prompt,
                        "original_prompt": image_prompt,
                    }
                )
            else:
                raise Exception(
                    f"Failed to download image from OpenAI: {response.status_code}"
                )

    except Exception as e:
        logger.error(f"Error generating story image: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Image generation failed: {str(e)}"}), 500


@app.route("/api/get-story-data/<session_id>", methods=["GET"])
def get_story_data(session_id):
    """Get story data for a session (for ZIP download)"""
    try:
        story_path = f"static/avatars/{session_id}/story.json"

        if not os.path.exists(story_path):
            return jsonify({"error": "Story data not found"}), 400

        with open(story_path, "r") as f:
            story_data = json.load(f)

        return jsonify({"success": True, "story": story_data})

    except Exception as e:
        logger.error(f"Error getting story data: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/generate-stream", methods=["POST"])
def generate_images_stream():
    """Initialize session and store only the avatar"""
    try:
        # Get uploaded avatar
        avatar_file = request.files["avatar"]
        if not avatar_file:
            return jsonify({"error": "No avatar file uploaded"}), 400

        # Get prompts from form - support dynamic number of prompts
        prompts = []
        prompt_index = 1

        # Keep collecting prompts until we find an empty one or reach a reasonable limit
        while prompt_index <= 20:  # Max 20 prompts for safety
            prompt_key = f"prompt_{prompt_index}"
            prompt = request.form.get(prompt_key, "").strip()
            if prompt:
                prompts.append(prompt)
                prompt_index += 1
            else:
                # Check if there are any more prompts after this empty one
                found_more = False
                for check_idx in range(prompt_index + 1, min(prompt_index + 5, 21)):
                    if request.form.get(f"prompt_{check_idx}", "").strip():
                        found_more = True
                        break

                if not found_more:
                    break
                else:
                    prompt_index += 1

        if not prompts:
            return jsonify({"error": "No prompts provided"}), 400

        # Create unique session directory for avatar only
        session_id = str(uuid.uuid4())
        output_dir = f"static/avatars/{session_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Store only the avatar locally
        avatar_path = os.path.join(output_dir, "avatar.jpg")
        avatar_file.save(avatar_path)

        return jsonify(
            {
                "session_id": session_id,
                "total_prompts": len(prompts),
                "prompts": prompts,
            }
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/generate-single/<session_id>/<int:idx>", methods=["POST"])
def generate_single_image(session_id, idx):
    """Generate a single image and return it as base64 without storing"""
    try:
        prompt = request.json.get("prompt")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        avatar_dir = f"static/avatars/{session_id}"
        avatar_path = os.path.join(avatar_dir, "avatar.jpg")

        if not os.path.exists(avatar_path):
            return jsonify({"error": "Avatar not found"}), 400

        # Enhance the prompt for character consistency
        enhanced_prompt = f"""
Transform the uploaded character/avatar into this scene: {prompt}

IMPORTANT INSTRUCTIONS:
- Use the uploaded avatar as the main character in this scene
- Maintain the character's distinctive features, clothing, and appearance
- The character should be clearly recognizable and prominent in the image
- Keep the character's proportions and style consistent
- Make sure the character fits naturally into the scene described
- Style: Child-friendly cartoon/illustration
- The character should be the hero/protagonist of this scene
"""

        print(f"Generating image {idx} with enhanced prompt...")

        # Always use OpenAI for image generation
        with open(avatar_path, "rb") as avatar_file_obj:
            result = client.images.edit(
                model="dall-e-2",
                image=avatar_file_obj,
                prompt=enhanced_prompt,
                size="1024x1024",
                n=1,
            )

            image_url = result.data[0].url

            # Download the image and convert to base64
            import requests

            response = requests.get(image_url)
            if response.status_code == 200:
                import base64

                image_base64 = base64.b64encode(response.content).decode("utf-8")

                print(f"Generated image {idx} - sending to frontend")

                # Return the image as base64 to frontend (no backend storage)
                return jsonify(
                    {
                        "success": True,
                        "image_base64": image_base64,
                        "filename": f"story_image_{idx}.jpg",
                        "prompt": enhanced_prompt,
                        "original_prompt": prompt,
                        "index": idx,
                    }
                )
            else:
                raise Exception(
                    f"Failed to download image from OpenAI: {response.status_code}"
                )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/get-avatar/<session_id>", methods=["GET"])
def get_avatar(session_id):
    """Get the avatar image as base64 for including in ZIP"""
    try:
        avatar_dir = f"static/avatars/{session_id}"
        avatar_path = os.path.join(avatar_dir, "avatar.jpg")

        if not os.path.exists(avatar_path):
            return jsonify({"error": "Avatar not found"}), 400

        # Read avatar and convert to base64
        with open(avatar_path, "rb") as avatar_file:
            avatar_base64 = base64.b64encode(avatar_file.read()).decode("utf-8")

        return jsonify(
            {"success": True, "avatar_base64": avatar_base64, "filename": "avatar.jpg"}
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/cleanup/<session_id>", methods=["POST"])
def cleanup_session(session_id):
    """Force delete entire session folder after ZIP download"""
    try:
        avatar_dir = f"static/avatars/{session_id}"

        # Force delete the entire session folder
        if os.path.exists(avatar_dir):
            try:
                # Try normal deletion first
                shutil.rmtree(avatar_dir)
                print(f"Successfully deleted session folder: {avatar_dir}")
                return jsonify(
                    {"success": True, "message": "Session folder deleted successfully"}
                )
            except PermissionError:
                # If folder is locked, try to force delete on Windows
                try:
                    import stat

                    # Make all files in the directory writable
                    for root, dirs, files in os.walk(avatar_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            os.chmod(file_path, stat.S_IWRITE)
                    shutil.rmtree(avatar_dir)
                    print(f"Force deleted locked session folder: {avatar_dir}")
                    return jsonify(
                        {
                            "success": True,
                            "message": "Session folder force deleted successfully",
                        }
                    )
                except Exception as force_error:
                    print(f"Force deletion failed: {str(force_error)}")
                    # Try alternative method - rename and delete
                    try:
                        import time

                        temp_name = f"{avatar_dir}_deleted_{int(time.time())}"
                        os.rename(avatar_dir, temp_name)
                        shutil.rmtree(temp_name)
                        print(f"Session folder deleted via rename method: {avatar_dir}")
                        return jsonify(
                            {
                                "success": True,
                                "message": "Session folder deleted via rename method",
                            }
                        )
                    except Exception as rename_error:
                        print(f"Rename deletion failed: {str(rename_error)}")
                        return jsonify(
                            {
                                "success": False,
                                "message": f"Could not delete session folder: {str(rename_error)}",
                            }
                        )
            except Exception as delete_error:
                print(f"Session folder deletion error: {str(delete_error)}")
                return jsonify(
                    {
                        "success": False,
                        "message": f"Session folder deletion failed: {str(delete_error)}",
                    }
                )
        else:
            print(f"Session folder not found: {avatar_dir}")
            return jsonify(
                {
                    "success": True,
                    "message": "Session folder not found (already deleted)",
                }
            )

    except Exception as e:
        print(f"Cleanup error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("static", exist_ok=True)
    os.makedirs("static/avatars", exist_ok=True)

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
