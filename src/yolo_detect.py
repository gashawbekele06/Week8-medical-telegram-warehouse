"""
YOLOv8 Object Detection for Telegram Medical Images
--------------------------------------------------
Scans downloaded images → detects objects → categorizes images
Saves results to data/yolo_results.csv

Run: uv run python src/yolo_detect.py
"""

import os
import csv
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO
import pandas as pd

# CONFIG

MODEL = YOLO("yolov8n.pt")  # nano model - fast & lightweight

IMAGE_ROOT = Path("data/raw/images")
OUTPUT_CSV = Path("data/yolo_results.csv")

# Classification rules based on COCO classes
PERSON_CLASS = "person"
PRODUCT_LIKE_CLASSES = {"bottle", "cup", "vase", "bowl",
                        "cell phone", "book"}  # approximate for pills/creams

# ─── MAIN DETECTION FUNCTION


def classify_image(detections):
    """Simple rule-based classification based on detected objects"""
    has_person = any(d["label"] == PERSON_CLASS for d in detections)
    has_product = any(d["label"] in PRODUCT_LIKE_CLASSES for d in detections)

    if has_person and has_product:
        return "promotional"      # person + product (showing/holding)
    elif has_product:
        return "product_display"  # only container/bottle
    elif has_person:
        return "lifestyle"        # person but no product
    else:
        return "other"

# PROCESS ALL IMAGES


results = []

for channel_dir in IMAGE_ROOT.iterdir():
    if not channel_dir.is_dir():
        continue

    channel_name = channel_dir.name

    for img_path in channel_dir.glob("*.[jJ][pP][gG]"):
        message_id = img_path.stem  # filename without extension = message_id

        print(f"Processing {img_path} ...")

        try:
            # Run YOLO detection
            preds = MODEL(img_path, verbose=False)[0]

            detected_objects = []
            for box in preds.boxes:
                cls_id = int(box.cls)
                label = preds.names[cls_id]
                conf = float(box.conf)
                detected_objects.append({
                    "label": label,
                    "confidence": round(conf, 4)
                })

            # Classify
            image_category = classify_image(detected_objects)

            results.append({
                "message_id": message_id,
                "channel_name": channel_name,
                "image_path": str(img_path.relative_to(IMAGE_ROOT.parent.parent)),
                "image_category": image_category,
                "detected_objects": detected_objects,  # list of dicts
                "processed_at": datetime.now().isoformat()
            })

        except Exception as e:
            print(f"Error on {img_path}: {e}")
            continue

# SAVE RESULTS

if results:
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nDone! Processed {len(results)} images.")
    print(f"Results saved to: {OUTPUT_CSV}")
else:
    print("No images found or processed.")
