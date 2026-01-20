"""
YOLOv8 Object Detection for Telegram Medical Images
--------------------------------------------------
Scans images from Task 1 -> detects objects -> classifies images -> saves to CSV

Run: uv run python src/yolo_detect.py

Output: data/yolo_results.csv
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(
        "logs/yolo_detect.log", encoding='utf-8'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

MODEL = YOLO("yolov8n.pt")  # nano model – fast & lightweight

IMAGE_ROOT = Path("data/raw/images")
OUTPUT_CSV = Path("data/yolo_results.csv")

# COCO classes we care about
PERSON = "person"
PRODUCT_LIKE = {"bottle", "cup", "vase", "bowl",
                "cell phone", "book"}  # proxies for containers/packages


def classify_image(detections):
    has_person = any(obj["label"] == PERSON for obj in detections)
    has_product = any(obj["label"] in PRODUCT_LIKE for obj in detections)

    if has_person and has_product:
        return "promotional"
    elif has_product:
        return "product_display"
    elif has_person:
        return "lifestyle"
    else:
        return "other"


def main():
    if not IMAGE_ROOT.exists():
        logger.error(f"Image directory not found: {IMAGE_ROOT}")
        return

    results = []

    for channel_folder in IMAGE_ROOT.iterdir():
        if not channel_folder.is_dir():
            continue

        channel = channel_folder.name
        logger.info(f"Processing channel: {channel}")

        for img_path in channel_folder.glob("*.[jJ][pP][gG]"):
            message_id = img_path.stem

            try:
                results_yolo = MODEL(img_path, verbose=False)[0]

                detected = []
                for box in results_yolo.boxes:
                    cls_id = int(box.cls)
                    label = results_yolo.names[cls_id]
                    conf = float(box.conf)
                    detected.append(
                        {"label": label, "confidence": round(conf, 4)})

                category = classify_image(detected)

                # Plain text, no Unicode arrow
                logger.info(f"{message_id} - Category: {category}")

                results.append({
                    "message_id": message_id,
                    "channel_name": channel,
                    "image_path": str(img_path.relative_to(IMAGE_ROOT.parent.parent)),
                    "image_category": category,
                    "detected_objects": json.dumps(detected),
                    "processed_at": datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"Error processing {img_path}: {str(e)}")
                continue

    if results:
        headers = ["message_id", "channel_name", "image_path",
                   "image_category", "detected_objects", "processed_at"]
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)

        logger.info(
            f"Processed {len(results)} images. Results saved to {OUTPUT_CSV}")
    else:
        logger.warning("No images processed.")


if __name__ == "__main__":
    main()
