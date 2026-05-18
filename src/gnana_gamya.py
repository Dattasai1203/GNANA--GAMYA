"""
Gnana Gamya — AI-Interfaced Interactive & Object-Detecting Robot
================================================================
A human-robot interaction (HRI) system that:
  - Detects people and objects in real-time (YOLOv5 via Ultralytics)
  - Greets users and listens to voice commands (SpeechRecognition)
  - Generates conversational responses (DialoGPT via Hugging Face)
  - Speaks responses aloud (pyttsx3)
  - Displays annotated video feed (OpenCV)

Authors : P. Anantha Padmanabban (11219H001)
          Dhulipala Datta Sai    (11219H003)
Guide   : Dr. T. Lakshmibai, Dr. T. Sundar
College : SCSVMV, Kanchipuram — Mechatronics Engineering, 2024-25 (Phase I)

Usage:
    python gnana_gamya.py

Controls:
    Press 'q' in the video window to exit.
"""

import cv2
import pyttsx3
import speech_recognition as sr
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import warnings

# Suppress noisy Hugging Face deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")

# ---------------------------------------------------------------------------
# Initialise core components
# ---------------------------------------------------------------------------

recognizer = sr.Recognizer()
engine = pyttsx3.init()

# DialoGPT — conversational language model
tokenizer = AutoTokenizer.from_pretrained(
    "microsoft/DialoGPT-medium",
    padding_side="left",
)
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# Move model to GPU if available, otherwise CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# YOLOv5 — real-time object detection
from ultralytics import YOLO  # noqa: E402  (import after warnings filter)
model_detection = YOLO("yolov5su.pt")  # auto-downloaded on first run


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def speak(text: str) -> None:
    """Convert a text string to spoken audio via pyttsx3."""
    engine.say(text)
    engine.runAndWait()


def listen() -> str:
    """
    Capture audio from the microphone and transcribe it via Google Web Speech API.

    Returns
    -------
    str
        Transcribed text, or an error message string if recognition fails.
    """
    with sr.Microphone() as source:
        print("Listening for a question or command...")
        audio = recognizer.listen(source)

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Error in request"


def get_response(text: str) -> str:
    """
    Generate a conversational response using DialoGPT.

    Parameters
    ----------
    text : str
        User's transcribed question or statement.

    Returns
    -------
    str
        Model-generated reply decoded into human-readable text.
    """
    inputs = tokenizer.encode(text + tokenizer.eos_token, return_tensors="pt").to(device)

    response_ids = model.generate(
        inputs,
        max_length=50,
        do_sample=True,
        top_k=40,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id,
    )

    response = tokenizer.decode(
        response_ids[:, inputs.shape[-1]:][0],
        skip_special_tokens=True,
    )
    return response


# ---------------------------------------------------------------------------
# Main detection + interaction loop
# ---------------------------------------------------------------------------

def detect_and_interact() -> None:
    """
    Main loop:
      1. Capture webcam frames continuously.
      2. Run YOLO object detection on each frame.
      3. If a person is detected, greet them and start a voice conversation.
      4. If only non-person objects are detected, announce what is seen.
      5. Display annotated video feed; exit cleanly on 'q' key press.
    """
    cap = cv2.VideoCapture(0)
    person_detected = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO inference on the current frame
        results = model_detection(frame)
        detected_objects = [
            model_detection.names[int(det[5])]
            for det in results[0].boxes.data.tolist()
        ]

        if "person" in detected_objects:
            # ---------------------------------------------------------------
            # Person path: greet once, then hold a voice conversation
            # ---------------------------------------------------------------
            if not person_detected:
                speak("Hello! How can I help you?")
                print("Gnana Gamya: Hello! How can I help you?")
                person_detected = True

            user_input = listen()
            print(f"User asked: {user_input}")

            if "stop" in user_input.lower():
                speak("Goodbye!")
                break

            response = get_response(user_input)
            print(f"Gnana Gamya says: {response}")
            speak(response)

        else:
            # ---------------------------------------------------------------
            # No person: announce any other detected objects
            # ---------------------------------------------------------------
            if detected_objects:
                objects_detected = ", ".join(detected_objects)
                print(f"Gnana Gamya sees: {objects_detected}")
                speak(f"Gnana Gamya sees: {objects_detected}")

            # Reset so a greeting fires again when the next person enters
            person_detected = False

        # Render annotated frame (bounding boxes + labels)
        annotated_frame = (
            results[0].plot()
            if hasattr(results[0], "plot")
            else frame
        )
        cv2.imshow("Gnana Gamya — Object Detection", annotated_frame)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    detect_and_interact()
