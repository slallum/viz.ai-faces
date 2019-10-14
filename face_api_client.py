import datetime
from urllib.parse import urljoin
import logging

from PIL import Image
import requests
import cachetools.func

import config

BASE_API_URL = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/'
AZURE_FACE_DETECT_STORE_TIME = datetime.timedelta(days=1)

logger = logging.getLogger(__name__)


def find_best_most_common_face(face_images_paths):
    """
    gets a list of face images paths
    finds the largest group of images with the same face,
    and returns the image with the largest face to image ratio from this group
    """
    if not face_images_paths:
        return None

    logger.info("getting faces details")
    face_id_to_details = {}
    for face_image_path in face_images_paths:
        width, height = Image.open(face_image_path).size
        face_details = get_face_details(face_image_path)
        face_id_to_details[face_details['faceId']] = {
            'path': face_image_path, 'image_size': width*height,
            'face_box_size': face_details['faceRectangle']['width'] * face_details['faceRectangle']['height'],
            'face_rectangle': face_details['faceRectangle'],
        }

    logger.info("getting most common face group")
    most_common_face_group = get_most_common_face_group(list(face_id_to_details.keys()))
    best_face_in_group = max(
        most_common_face_group,
        key=lambda face: face_id_to_details[face]['face_box_size'] / face_id_to_details[face]['image_size']
    )

    return face_id_to_details[best_face_in_group]


# the face id is saved in azure, that's why we can cache this function and get a better performance
@cachetools.func.ttl_cache(maxsize=1e6, ttl=AZURE_FACE_DETECT_STORE_TIME.total_seconds())
def get_face_details(face_image_path):
    """
    gets face details from face image path
    uses face detect endpoint: https://westus.dev.cognitive.microsoft.com/docs/services/563879b61984550e40cbbe8d/operations/563879b61984550f30395236
    """
    face_details = _face_api_call('post', 'detect', data=open(face_image_path, 'rb').read(),
                                  headers={'Content-Type': 'application/octet-stream'})
    return face_details[0]


def get_most_common_face_group(face_ids):
    """
    gets a list of azure face ids and returns the largest group of face ids that belong same face
    uses face group endpoint: https://westus.dev.cognitive.microsoft.com/docs/services/563879b61984550e40cbbe8d/operations/563879b61984550f30395238
    """
    if not face_ids:
        return []

    group_response = _face_api_call('post', 'group', json={"faceIds": face_ids})
    groups, ungrouped_images = group_response['groups'], group_response['messyGroup']
    if not groups:
        # each image is of a different person, so just return the first image as the "largest" group
        return [ungrouped_images[0]]

    return max(groups, key=len)


def _face_api_call(request_type, path, **kwargs):
    """
    request_type: "get" or "post"
    path: api path
    kwargs: can be any arguments the request call gets
    """
    request_function = getattr(requests, request_type.lower())
    response = request_function(
        urljoin(BASE_API_URL, path),
        headers={"Ocp-Apim-Subscription-Key": config.AZURE_FACE_KEY, **kwargs.pop('headers', {})},
        **kwargs
    )
    response_json = response.json()

    if 'error' in response_json:
        if response_json['error'].get('code') == '429':
            raise FaceAPIRateLimit(response_json['error'])
        raise FaceAPIError(response_json['error'])

    return response.json()


class FaceAPIError(Exception):
    pass


class FaceAPIRateLimit(FaceAPIError):
    pass

