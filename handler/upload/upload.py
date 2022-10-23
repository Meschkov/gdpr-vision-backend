import base64
import uuid
import cv2
from google.cloud import storage
from onerecord.models.cargo import Shipment
from onerecord.models.cargo import ExternalReference
from onerecord.client import ONERecordClient

from .image import label_image, blur_image

client = ONERecordClient(host="team-gdpr.one-record.de", port=443, ssl=True, company_identifier="gdpr")


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    return blob.public_url


def set_onerecord_external_reference(uri: str, img_path: str):
    lo: Shipment = client.get_logistics_object_by_uri(uri)
    print(lo.external_references)
    external_reference = ExternalReference(**{
        "document_name": "Photo of piece",
        "document_link": img_path,
        "document_type": "photo"
    })
    lo.external_references = [external_reference]
    print(lo.external_references)
    client.update_logistics_object(lo)


def upload_image(request_body: dict) -> tuple[str, int]:
    # Store to .jpg to /tmp
    tmp_image_file_path: str = f"/tmp/{uuid.uuid4()}.jpeg"
    with open(tmp_image_file_path, "wb") as f:
        s: str = request_body['photo']
        b: bytes = base64.decodebytes(s.encode('utf-8'))
        f.write(b)

    labels = label_image(tmp_image_file_path)
    if len(labels) > 0:
        blurred_image = blur_image(tmp_image_file_path, labels)

        tmp_blurred_image_file_path: str = f"/tmp/{uuid.uuid4()}-blurred.jpeg"
        rotated_image = cv2.rotate(blurred_image, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite(tmp_blurred_image_file_path, rotated_image)

        public_url = upload_blob("gdpr-blurred-images", tmp_blurred_image_file_path, f"{uuid.uuid4()}.jpeg")
    else:
        public_url = upload_blob("gdpr-original-images", tmp_image_file_path, f"{uuid.uuid4()}.jpeg")

    # set_onerecord_external_reference(request_body["uri"], public_url)
    return "OK", 200
