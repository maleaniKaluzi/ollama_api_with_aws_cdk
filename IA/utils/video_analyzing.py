import cv2, requests, os, tempfile, gc
import base64
from .img_analyzing import describe_image
from .prompts.video_prompt import VideoPrompt

OLLAMA_URL = "http://localhost:11434"
MODEL = "llava"


def extract_frames(video_path: str, every_x_seconds: int = 2, max_frames: int = 20):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    frames_base64 = []
    frame_interval = int(fps * every_x_seconds)
    frame_count = 0
    extracted = 0

    while cap.isOpened() and extracted < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            _, buffer = cv2.imencode(".jpg", frame)
            image_bytes = buffer.tobytes()
            encoded = base64.b64encode(image_bytes).decode("utf-8")
            frames_base64.append(encoded)
            extracted += 1

        frame_count += 1

    cap.release()

    return frames_base64


# frames_base64
def analyze_video(video_bytes):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.write(video_bytes)
    tmp.close()

    cap = cv2.VideoCapture(tmp.name)
    fps = cap.get(cv2.CAP_PROP_FPS)  # 1 sec 30 images, 30 x 30
    step = int(fps * 4)  # 30 x 4; 30 sec : 0, 120, 240, 360 ... 1G; 5 min

    raw_frame_texts = []
    count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if count % step == 0:
            frame = cv2.resize(frame, (640, 480))
            _, buf = cv2.imencode(".jpg", frame)

            res = describe_image(buf.tobytes())
            raw_frame_texts.append(f"Time {count//fps}s: {res['description']}")

            del buf
            gc.collect()
        count += 1

    cap.release()
    os.unlink(tmp.name)

    final_prompt = VideoPrompt.get_prompt("\n".join(raw_frame_texts))

    response = requests.post(
        # f"{OLLAMA_URL}/api/chat",
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": MODEL,
            "format": "json",
            "prompt": "decris moi exactement toutes les scene que tu vois dans cette video",
            # "messages": [{"role": "user", "content": final_prompt}],
            "stream": False,
            "options": {"temperature": 0},
        },
        # timeout=5000
    )

    return response.json()
    # return response.json()["message"]["content"]
