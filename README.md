# viz.ai-faces
*Take home project from Viz.ai.*  
A rest API for getting the "best most common face" in a group of face photos.  
The API's relevant endpoint is `/best_most_common_face`.


## Installation
The project uses python3
```
pip install -r requirements.txt
```

## Running the app
```
python app.py
```

## Using the app from a client
You can use the app from curl or any other http client. Example with output:

```
$ curl -X POST http://localhost:8000/best_most_common_face -H "Content-Type: application/json" -d '["sample_images/a.jpeg", "sample_images/b.jpeg", "sample_images/c.jpeg", "sample_images/d.jpeg", "sample_images/e.jpeg", "sample_images/f.jpeg", "sample_images/g.jpeg", "sample_images/e2.jpeg"]'`
{"face_box_size":46225,"face_rectangle":{"height":215,"left":140,"top":134,"width":215},"image_size":177600,"path":"sample_images/e2.jpeg"}
```
(There are sample_images directory in the project for an easy use).
## Running the tests:
`pytest tests/`

The tests are using vcrpy cassettes, that recorded Azure face api's responses.  
Also, each test clears the cached method's cache, to make sure it runs "from scratch".
