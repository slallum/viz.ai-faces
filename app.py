import logging

from flask import Flask, request, jsonify

from face_api_client import find_best_most_common_face

app = Flask(__name__)


@app.route('/best_most_common_face', methods=['POST'])
def best_most_common_face():
    face_list = request.json
    try:
        return jsonify(find_best_most_common_face(face_list))
    except Exception as exc:
        return jsonify({'error': exc.args}), 500


def main():
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
