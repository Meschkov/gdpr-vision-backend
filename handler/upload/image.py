import io
import cv2
import proto
import numpy as np

from google.cloud import vision

from PIL import Image


def label_image(img_path: str) -> proto.marshal.collections.repeated.RepeatedComposite:
    vision_client = vision.ImageAnnotatorClient()
    with open(img_path, "rb") as f:
        img = f.read()

    image = vision.Image(content=img)
    response = vision_client.face_detection(image=image)
    faces = response.face_annotations
    return faces


def blur_image(img_path: str, labels: proto.marshal.collections.repeated.RepeatedComposite):
    with open(img_path, "rb") as f:
        image = f.read()
    img = Image.open(io.BytesIO(image))
    img = np.array(img)
    # RGB/BGR channel flip for PIL-OpenCV compatibility
    img = img[:, :, ::-1]
    for label in labels:
        box = [(vertex.x, vertex.y)
               for vertex in label.bounding_poly.vertices]
        top_left = box[0]
        bottom_right = box[2]
        x = top_left[0]
        y = top_left[1]
        w = bottom_right[0] - top_left[0]
        h = bottom_right[1] - top_left[1]

        roi = img[y:y + h, x:x + w]
        roi_blurred = cv2.blur(roi, (100, 100))
        img[y:y + h, x:x + w] = roi_blurred

    return img
