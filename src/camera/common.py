from __future__ import annotations
import numpy as np
import cv2


class ReadFrameException(Exception):
    pass


class EncodeImageException(Exception):
    pass


def image_put_text(
    image: np.ndarray,
    text: str,
    bottom_left_point: list[int]
) -> np.ndarray:
    image = cv2.putText(
        img=image,
        text=text,
        org=bottom_left_point,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1,
        color=(0, 0, 0),
        thickness=3
    )
    image = cv2.putText(
        img=image,
        text=text,
        org=bottom_left_point,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1,
        color=(255, 255, 255),
        thickness=2
    )
    return image


def encode_image(image: np.ndarray) -> bytes:
    flag, image = cv2.imencode('.jpg', image)
    if flag:
        return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(image) + b'\r\n'
    else:
        raise EncodeImageException("Encode image error")
