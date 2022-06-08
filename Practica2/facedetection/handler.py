import cv2
import requests
import numpy as np
import base64

xmlFile = "haarcascade_frontalface_default.xml"

def handle(req):
    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + xmlFile)

    # Get the image from an URL
    imgBytes = requests.get(req).content
    arr = np.asarray(bytearray(imgBytes), dtype=np.uint8)
    img = cv2.imdecode(arr, -1) # 'Load it as it is'
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    #print("Found {0} faces!".format(len(faces)))
    #return str(len(faces))

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    jpg_img = cv2.imencode('.jpg', img)
    b64_string = base64.b64encode(jpg_img[1]).decode('utf-8')

    return("<img src=\"data:image/png;base64, " + b64_string + "\">")
