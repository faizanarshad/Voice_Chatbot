"""
OpenCV image preprocessing before AI vision analysis.
Improves image quality and reduces API cost.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Config
MAX_DIMENSION = 1024  # Resize if larger; reduces API tokens
JPEG_QUALITY = 85
DENOISE_STRENGTH = 10  # For fastNlMeansDenoisingColored


def preprocess_for_vision(image_bytes: bytes) -> bytes:
    """
    Preprocess image before sending to vision API:
    - Resize: downsample large images to reduce API cost
    - Denoise: reduce noise in low-light/blurry photos
    - Contrast/brightness: improve visibility
    - Format: normalize to JPEG for API compatibility
    """
    # Temporary print - verify preprocessing runs before image analysis
    print(f">>> [Image Preprocessing] Input: {len(image_bytes)} bytes")

    if not OPENCV_AVAILABLE:
        logger.debug("OpenCV not available, skipping preprocessing")
        print(">>> [Image Preprocessing] OpenCV not available, skipping")
        return image_bytes

    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            logger.warning("OpenCV could not decode image")
            print(">>> [Image Preprocessing] Could not decode image")
            return image_bytes

        h, w = img.shape[:2]
        if h == 0 or w == 0:
            return image_bytes

        # 1. Resize if too large
        if max(h, w) > MAX_DIMENSION:
            scale = MAX_DIMENSION / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            logger.debug(f"Resized image from {w}x{h} to {new_w}x{new_h}")
            print(f">>> [Image Preprocessing] Resized {w}x{h} -> {new_w}x{new_h}")

        # 2. Denoise (skip for very small images)
        if min(img.shape[:2]) >= 100:
            try:
                img = cv2.fastNlMeansDenoisingColored(
                    img, None, DENOISE_STRENGTH, DENOISE_STRENGTH, 7, 21
                )
            except cv2.error:
                pass  # Fallback if denoise fails

        # 3. Contrast/brightness - CLAHE for better visibility
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        img = cv2.merge([l, a, b])
        img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)

        # 4. Format conversion - encode to JPEG
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
        success, buf = cv2.imencode(".jpg", img, encode_params)
        if success:
            result = buf.tobytes()
            print(f">>> [Image Preprocessing] Output: {len(result)} bytes (resize+denoise+contrast+JPEG)")
            return result
        return image_bytes

    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}, using original")
        print(f">>> [Image Preprocessing] Failed: {e}, using original")
        return image_bytes
