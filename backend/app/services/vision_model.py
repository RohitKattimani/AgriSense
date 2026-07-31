"""
Crop disease / pest detection using a pretrained HuggingFace image
classification model.

Real model: linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification
(fine-tuned on PlantVillage - 38 classes covering apple, corn, grape,
potato, tomato, etc. diseases + healthy states). Any HF image-classification
checkpoint can be swapped in via VISION_MODEL_ID in .env.

The pipeline is lazy-loaded once and cached. If transformers/torch or the
model weights aren't available (e.g. no internet on first run), the
service transparently falls back to a lightweight mock classifier so the
rest of the app keeps working end-to-end during development/demo.
"""
from __future__ import annotations
import io
import logging
import random
from functools import lru_cache
from typing import List, Dict

from PIL import Image

from app.config import settings

logger = logging.getLogger("agrisense.vision")

# A representative slice of PlantVillage-style labels, used both to make
# the mock fallback plausible and to build human-readable remedy hints.
KNOWN_CLASSES = [
    "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot", "Tomato___healthy",
    "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
    "Corn___Common_rust", "Corn___Northern_Leaf_Blight", "Corn___healthy",
    "Grape___Black_rot", "Grape___Esca", "Grape___healthy",
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___healthy",
    "Pepper__bell___Bacterial_spot", "Pepper__bell___healthy",
]

REMEDY_HINTS: Dict[str, str] = {
    "Early_blight": "Caused by Alternaria fungus. Remove infected lower leaves, "
                    "avoid overhead watering, apply a copper-based or chlorothalonil fungicide, "
                    "and rotate crops next season.",
    "Late_blight": "Fast-spreading and destructive (Phytophthora). Remove and destroy "
                    "infected plants immediately, improve airflow, and apply a "
                    "protectant fungicide (e.g. mancozeb) before rain events.",
    "Leaf_Mold": "Favoured by high humidity. Increase ventilation, avoid wetting "
                 "foliage, and use a sulfur or copper fungicide if it spreads.",
    "Septoria_leaf_spot": "Fungal spots with dark borders. Remove affected leaves, "
                          "mulch to stop soil splash, and rotate crops.",
    "Common_rust": "Orange-brown pustules. Usually manageable with resistant "
                   "varieties next season; fungicide only needed if severe and early.",
    "Northern_Leaf_Blight": "Cigar-shaped grey lesions. Use resistant hybrids, "
                            "till residue after harvest, apply fungicide if severe.",
    "Black_rot": "Fungal disease common in warm, wet weather. Prune for airflow, "
                 "remove mummified fruit, apply fungicide during flowering.",
    "Esca": "Also called 'measles'. No cure once systemic - remove and destroy "
            "severely infected vines, avoid pruning wounds in wet weather.",
    "Apple_scab": "Olive-green to black spots on leaves/fruit. Rake and destroy "
                  "fallen leaves, apply fungicide at green-tip stage next spring.",
    "Bacterial_spot": "Small water-soaked spots. Avoid overhead irrigation, use "
                      "copper-based bactericide, avoid working fields when wet.",
    "healthy": "No disease symptoms detected. Keep up good watering, spacing and "
               "nutrient practices, and continue periodic scouting.",
}


def _hint_for_label(label: str) -> str:
    for key, hint in REMEDY_HINTS.items():
        if key.lower() in label.lower():
            return hint
    return "Monitor the plant closely over the next few days and rescan if symptoms change."


@lru_cache(maxsize=1)
def _load_pipeline():
    """Lazily load and cache the HF image-classification pipeline."""
    from transformers import pipeline
    logger.info(f"Loading vision model '{settings.VISION_MODEL_ID}' ...")
    clf = pipeline(
        "image-classification",
        model=settings.VISION_MODEL_ID,
        token=settings.HF_TOKEN,
        device=-1 if settings.VISION_DEVICE == "cpu" else 0,
    )
    logger.info("Vision model loaded.")
    return clf


def _mock_classify(image_bytes: bytes) -> List[Dict]:
    """
    Deterministic-ish mock classifier used when the real HF model can't be
    loaded (e.g. no internet). Picks a label based on a hash of the image
    bytes so the same image always returns the same result, and returns a
    plausible confidence distribution.
    """
    seed = sum(image_bytes[:4096]) if image_bytes else 0
    rng = random.Random(seed)
    primary = rng.choice(KNOWN_CLASSES)
    primary_conf = round(rng.uniform(0.68, 0.95), 4)
    remaining = 1 - primary_conf
    others = rng.sample([c for c in KNOWN_CLASSES if c != primary], 2)
    o1 = round(remaining * rng.uniform(0.4, 0.7), 4)
    o2 = round(remaining - o1, 4)
    return [
        {"label": primary, "score": primary_conf},
        {"label": others[0], "score": o1},
        {"label": others[1], "score": o2},
    ]


def classify_image(image_bytes: bytes, top_k: int = 3) -> Dict:
    """
    Classify a single leaf/plant photo.
    Returns: {
        "predictions": [{"label", "score"}, ...],
        "top_label", "top_confidence", "crop", "condition",
        "is_healthy", "remedy_hint", "model_source"
    }
    """
    model_source = "huggingface"
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        clf = _load_pipeline()
        raw = clf(image, top_k=top_k)
        predictions = [{"label": r["label"], "score": round(float(r["score"]), 4)} for r in raw]
    except Exception as e:
        logger.warning(f"Falling back to mock vision classifier: {e}")
        model_source = "mock (offline fallback)"
        predictions = _mock_classify(image_bytes)[:top_k]

    top = predictions[0]
    label = top["label"]
    parts = label.replace("__", "_").split("_")
    crop = parts[0].strip("_") if parts else "Unknown"
    is_healthy = "healthy" in label.lower()
    condition = "Healthy" if is_healthy else label.split("___")[-1].replace("_", " ") if "___" in label else label.replace("_", " ")

    return {
        "predictions": predictions,
        "top_label": label,
        "top_confidence": top["score"],
        "crop": crop,
        "condition": condition,
        "is_healthy": is_healthy,
        "remedy_hint": _hint_for_label(label),
        "model_source": model_source,
    }
