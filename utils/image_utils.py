import cv2
import numpy as np
from fastapi import HTTPException, status

def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    """Decodes a raw byte stream into an OpenCV BGR numpy array."""
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Failed to decode image buffer. Invalid image."
            )
        return img
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=f"Image decoding error: {str(e)}"
        )