import os
import base64
import shutil
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from PIL import Image
from io import BytesIO
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load your OpenAI API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.route("/")
def index():
    return render_template("index.html")


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

        print(f"Generating image {idx}...")

        # Open the saved avatar file exactly like main.py does
        with open(avatar_path, "rb") as avatar_file_obj:
            # Pass the file object directly - EXACT same as main.py
            result = client.images.edit(
                model="gpt-image-1",
                image=avatar_file_obj,
                prompt=prompt,
                size="1024x1024",
                output_format="jpeg",
            )

            # Get the base64 image directly from API response
            image_base64 = result.data[0].b64_json

            print(f"Generated image {idx} - sending to frontend")

            # Return the image as base64 to frontend (no backend storage)
            return jsonify(
                {
                    "success": True,
                    "image_base64": image_base64,
                    "filename": f"story_image_{idx}.jpg",
                    "prompt": prompt,
                    "index": idx,
                }
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

    # This is required by Vercel's serverless handler


def handler(environ, start_response):
    return app.wsgi_app(environ, start_response)


if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("static", exist_ok=True)
    os.makedirs("static/avatars", exist_ok=True)

    # Use PORT environment variable for Render deployment, fallback to 10000 for local development
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
