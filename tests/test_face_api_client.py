from pathlib import Path

import vcr
from pytest import fixture

from face_api_client import find_best_most_common_face, get_face_details

PROJECT_DIR = Path(__file__).parent.parent


@fixture(autouse=True)
def clearcache():
    # make sure each test runs from the start, without using the cache
    get_face_details.cache_clear()


@vcr.use_cassette("cassettes/multiple_groups.yml")
def test_find_best_most_common_face_with_multiple_groups():
    result = find_best_most_common_face([
        PROJECT_DIR / 'sample_images/e.jpeg', PROJECT_DIR / 'sample_images/e2.jpeg', PROJECT_DIR / 'sample_images/d.jpeg',
        PROJECT_DIR / 'sample_images/a.jpeg', PROJECT_DIR / 'sample_images/b.jpeg'
    ])
    assert result == {'path': PROJECT_DIR / 'sample_images/e2.jpeg', 'image_size': 177600, 'face_box_size': 46225,
                      'face_rectangle': {'height': 215, 'left': 140, 'top': 134, 'width': 215}}


@vcr.use_cassette("cassettes/different_faces.yml")
def test_find_best_most_common_face_different_faces():
    result = find_best_most_common_face([PROJECT_DIR / 'sample_images/a.jpeg', PROJECT_DIR / 'sample_images/b.jpeg'])
    assert result == {'path': PROJECT_DIR / 'sample_images/b.jpeg', 'image_size': 277800, 'face_box_size': 54756,
                      'face_rectangle': {'height': 234, 'left': 207, 'top': 179, 'width': 234}}


def test_find_best_most_common_face_no_images():
    result = find_best_most_common_face([])
    assert result is None
