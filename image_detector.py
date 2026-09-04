"""Image Hazard Detection - YOLOv8/CLIP-based PPE and hazard detection from uploaded photos."""
import os
import io
import base64
from typing import Optional

# Hazard detection classes
PPE_CLASSES = [
    "hard_hat", "safety_vest", "gloves", "safety_boots",
    "goggles", "face_mask", "harness", "ear_protection"
]

HAZARD_CLASSES = [
    "oil_spill", "smoke", "fire", "corroded_pipe",
    "missing_guard_rail", "exposed_wiring", "fallen_object",
    "chemical_leak", "blocked_exit", "trip_hazard"
]

UNSAFE_ACT_CLASSES = [
    "no_hard_hat", "no_safety_vest", "no_gloves",
    "improper_climbing", "working_without_harness",
    "smoking_near_equipment", "using_phone_while_operating"
]


def detect_hazards_from_image(image_bytes: bytes, filename: str = "") -> dict:
    """
    Detect safety hazards from an uploaded image.
    Uses CLIP for zero-shot classification when available,
    falls back to template-based detection.
    """
    # Try CLIP-based detection
    try:
        return _detect_with_clip(image_bytes, filename)
    except Exception as e:
        print(f"[image] CLIP detection failed ({e}), using template")
        return _detect_template(image_bytes, filename)


def _detect_with_clip(image_bytes: bytes, filename: str) -> dict:
    """Use OpenAI CLIP for zero-shot hazard detection."""
    try:
        import torch
        from PIL import Image
        from transformers import CLIPProcessor, CLIPModel

        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Combine all hazard-related text prompts
        all_labels = (
            [f"photo of {c.replace('_', ' ')}" for c in HAZARD_CLASSES] +
            [f"person wearing {c.replace('_', ' ')}" for c in PPE_CLASSES] +
            [f"person doing {c.replace('_', ' ')}" for c in UNSAFE_ACT_CLASSES] +
            ["safe industrial workplace", "unsafe industrial workplace"]
        )

        inputs = processor(text=all_labels, images=image, return_tensors="pt", padding=True)
        outputs = model(**inputs)
        logits = outputs.logits_per_image[0]
        probs = logits.softmax(dim=0).detach().numpy()

        # Get top detections
        detections = []
        for idx in probs.argsort()[-8:][::-1]:
            prob = float(probs[idx])
            if prob > 0.05:
                label = all_labels[idx]
                category = "hazard" if idx < len(HAZARD_CLASSES) else "ppe" if idx < len(HAZARD_CLASSES) + len(PPE_CLASSES) else "unsafe_act"
                detections.append({
                    "label": label.replace("photo of ", "").replace("person wearing ", "").replace("person doing ", ""),
                    "category": category,
                    "confidence": round(prob * 100, 1),
                })

        # Determine overall safety status
        hazard_dets = [d for d in detections if d["category"] == "hazard" or d["category"] == "unsafe_act"]
        ppe_dets = [d for d in detections if d["category"] == "ppe"]

        if hazard_dets and hazard_dets[0]["confidence"] > 20:
            safety_status = "UNSAFE"
        elif any("unsafe" in d["label"] for d in detections):
            safety_status = "UNSAFE"
        else:
            safety_status = "SAFE"

        return {
            "safety_status": safety_status,
            "detections": detections,
            "hazards_found": hazard_dets,
            "ppe_detected": ppe_dets,
            "method": "CLIP zero-shot",
            "filename": filename,
        }

    except ImportError:
        raise Exception("transformers/PIL not installed")


def _detect_template(image_bytes: bytes, filename: str) -> dict:
    """Template-based detection when CLIP is not available."""
    file_size = len(image_bytes)
    ext = filename.lower().split(".")[-1] if "." in filename else "unknown"

    # Simulated detection based on file characteristics
    # In production, this would use YOLOv8 or similar
    detections = []

    # Basic heuristics for demo
    if ext in ["jpg", "jpeg", "png"]:
        detections = [
            {"label": "industrial scene detected", "category": "context", "confidence": 85.0},
            {"label": "scene analysis requires CLIP model", "category": "info", "confidence": 100.0},
        ]

    return {
        "safety_status": "NEEDS_REVIEW",
        "detections": detections,
        "hazards_found": [],
        "ppe_detected": [],
        "method": "template (install transformers+torch for CLIP)",
        "filename": filename,
        "setup_command": "pip install transformers torch Pillow",
    }


def get_detection_summary(detection_result: dict) -> str:
    """Generate a human-readable summary of the detection."""
    status = detection_result.get("safety_status", "UNKNOWN")
    hazards = detection_result.get("hazards_found", [])
    ppe = detection_result.get("ppe_detected", [])

    if status == "UNSAFE":
        summary = f"HAZARD DETECTED: {len(hazards)} hazard(s) found. "
        for h in hazards[:3]:
            summary += f"- {h['label']} ({h['confidence']}% confidence). "
        if not ppe:
            summary += "No PPE detected. "
        summary += "Immediate review recommended."
    elif status == "SAFE":
        summary = f"Scene appears safe. {len(ppe)} PPE item(s) detected. "
        for p in ppe[:3]:
            summary += f"{p['label']}, "
    else:
        summary = "Image received. Full analysis requires CLIP model (pip install transformers torch). "
        summary += detection_result.get("setup_command", "")

    return summary
