import numpy as np
import cv2


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
