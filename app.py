import os
import base64
import zipfile
import shutil
import atexit
import time
from flask import (
    Flask,
    render_template,
    request,
    send_file,
    jsonify,
    after_this_request,
)
from openai import OpenAI
from PIL import Image
from io import BytesIO
import tempfile
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load your OpenAI API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Track active sessions for cleanup
active_sessions = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_images():
    try:
        # Get uploaded avatar
        avatar_file = request.files["avatar"]
        if not avatar_file:
            return jsonify({"error": "No avatar file uploaded"}), 400

        # Get prompts from form
        prompts = []
        for i in range(1, 6):
            prompt = request.form.get(f"prompt_{i}", "").strip()
            if prompt:
                prompts.append(prompt)

        if not prompts:
            return jsonify({"error": "No prompts provided"}), 400

        # Create unique session directory
        session_id = str(uuid.uuid4())
        output_dir = f"static/generated/{session_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Track this session
        active_sessions[session_id] = {"created": time.time(), "output_dir": output_dir}

        # Store avatar locally first (exactly like main.py approach)
        avatar_path = os.path.join(output_dir, "avatar.jpg")
        avatar_file.save(avatar_path)

        generated_images = []

        # Generate images using the EXACT same logic as main.py
        for idx, prompt in enumerate(prompts, 1):
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

                # Decode the base64 image - EXACT same as main.py
                image_base64 = result.data[0].b64_json
                image_bytes = base64.b64decode(image_base64)
                image = Image.open(BytesIO(image_bytes))

                # Save the image - EXACT same as main.py
                filename = f"story_image_{idx}.jpg"
                out_path = os.path.join(output_dir, filename)
                image.save(out_path, format="JPEG", quality=90)

                generated_images.append(
                    {
                        "filename": filename,
                        "path": f"generated/{session_id}/{filename}",
                        "prompt": prompt,
                    }
                )

                print(f"Saved: {out_path}")

        # Add avatar to the generated images list so it's included in zip
        generated_images.append(
            {
                "filename": "avatar.jpg",
                "path": f"generated/{session_id}/avatar.jpg",
                "prompt": "Original avatar image",
            }
        )

        return jsonify(
            {"success": True, "session_id": session_id, "images": generated_images}
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/generate-stream", methods=["POST"])
def generate_images_stream():
    """Generate images one by one and return each as it's completed"""
    try:
        # Get uploaded avatar
        avatar_file = request.files["avatar"]
        if not avatar_file:
            return jsonify({"error": "No avatar file uploaded"}), 400

        # Get prompts from form
        prompts = []
        for i in range(1, 6):
            prompt = request.form.get(f"prompt_{i}", "").strip()
            if prompt:
                prompts.append(prompt)

        if not prompts:
            return jsonify({"error": "No prompts provided"}), 400

        # Create unique session directory
        session_id = str(uuid.uuid4())
        output_dir = f"static/generated/{session_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Track this session
        active_sessions[session_id] = {"created": time.time(), "output_dir": output_dir}

        # Store avatar locally first
        avatar_path = os.path.join(output_dir, "avatar.jpg")
        avatar_file.save(avatar_path)

        return jsonify({"session_id": session_id, "total_prompts": len(prompts)})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/generate-single/<session_id>/<int:idx>", methods=["POST"])
def generate_single_image(session_id, idx):
    """Generate a single image for the given session and index"""
    try:
        prompt = request.json.get("prompt")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        output_dir = f"static/generated/{session_id}"
        avatar_path = os.path.join(output_dir, "avatar.jpg")

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

            # Decode the base64 image - EXACT same as main.py
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))

            # Save the image - EXACT same as main.py
            filename = f"story_image_{idx}.jpg"
            out_path = os.path.join(output_dir, filename)
            image.save(out_path, format="JPEG", quality=90)

            print(f"Saved: {out_path}")

            return jsonify(
                {
                    "success": True,
                    "filename": filename,
                    "path": f"generated/{session_id}/{filename}",
                    "prompt": prompt,
                    "index": idx,
                }
            )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/download/<session_id>")
def download_zip(session_id):
    try:
        # Create zip file
        zip_path = f"static/generated/{session_id}.zip"
        image_dir = f"static/generated/{session_id}"

        if not os.path.exists(image_dir):
            return jsonify({"error": "Session not found"}), 404

        # Create zip with all files (including avatar)
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for filename in os.listdir(image_dir):
                if filename.endswith(
                    (".jpg", ".jpeg", ".png")
                ):  # Include all image files
                    file_path = os.path.join(image_dir, filename)
                    zipf.write(file_path, filename)

        # Ensure cleanup happens after the response is sent
        @after_this_request
        def cleanup_files(response):
            try:
                # Remove the session directory (contains avatar and generated images)
                if os.path.exists(image_dir):
                    shutil.rmtree(image_dir)
                    print(f"Cleaned up directory: {image_dir}")

                # Remove the zip file
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                    print(f"Cleaned up zip file: {zip_path}")

                # Remove from active sessions tracking
                if session_id in active_sessions:
                    del active_sessions[session_id]
                    print(f"Removed session {session_id} from tracking")

            except Exception as e:
                print(f"Cleanup error: {str(e)}")

            return response

        # Send the zip file
        return send_file(
            zip_path, as_attachment=True, download_name=f"story_images_{session_id}.zip"
        )

    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/cleanup/<session_id>", methods=["POST"])
def cleanup_session(session_id):
    """Manual cleanup endpoint that can be called when browser is closed"""
    try:
        cleanup_session_files(session_id)
        return jsonify({"success": True, "message": f"Session {session_id} cleaned up"})
    except Exception as e:
        print(f"Manual cleanup error: {str(e)}")
        return jsonify({"error": str(e)}), 500


def cleanup_session_files(session_id):
    """Helper function to clean up session files"""
    try:
        # Remove session directory
        image_dir = f"static/generated/{session_id}"
        if os.path.exists(image_dir):
            shutil.rmtree(image_dir)
            print(f"Cleaned up directory: {image_dir}")

        # Remove zip file if it exists
        zip_path = f"static/generated/{session_id}.zip"
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"Cleaned up zip file: {zip_path}")

        # Remove from active sessions tracking
        if session_id in active_sessions:
            del active_sessions[session_id]
            print(f"Removed session {session_id} from tracking")

    except Exception as e:
        print(f"Cleanup error for session {session_id}: {str(e)}")


def cleanup_old_sessions():
    """Clean up sessions older than 1 hour"""
    current_time = time.time()
    sessions_to_cleanup = []

    for session_id, session_data in active_sessions.items():
        # If session is older than 1 hour (3600 seconds)
        if current_time - session_data["created"] > 3600:
            sessions_to_cleanup.append(session_id)

    for session_id in sessions_to_cleanup:
        print(f"Cleaning up old session: {session_id}")
        cleanup_session_files(session_id)


@app.route("/cleanup-old", methods=["POST"])
def cleanup_old_sessions_endpoint():
    """Endpoint to manually trigger cleanup of old sessions"""
    try:
        cleanup_old_sessions()
        return jsonify({"success": True, "message": "Old sessions cleaned up"})
    except Exception as e:
        print(f"Old sessions cleanup error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Clean up any remaining files when the app shuts down
@atexit.register
def cleanup_on_exit():
    """Clean up all active sessions when the app shuts down"""
    print("Cleaning up all sessions on app shutdown...")
    for session_id in list(active_sessions.keys()):
        cleanup_session_files(session_id)


if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("static", exist_ok=True)
    os.makedirs("static/generated", exist_ok=True)

    # Clean up any leftover files from previous runs
    generated_dir = "static/generated"
    if os.path.exists(generated_dir):
        for item in os.listdir(generated_dir):
            item_path = os.path.join(generated_dir, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                print(f"Cleaned up leftover: {item_path}")
            except Exception as e:
                print(f"Error cleaning up {item_path}: {e}")

    app.run(debug=True)
