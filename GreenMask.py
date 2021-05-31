import numpy as np
import cv2

cap = cv2.VideoCapture(0)

lower_green = np.array([40, 100, 100])
upper_green = np.array([100, 255, 255])

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # convert image into gray
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # converts to HSV format
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # detect only green
    mask = cv2.inRange(image, lower_green, upper_green)
    res = cv2.bitwise_and(image, image, mask=mask)

    # flip image
    # image = cv2.flip(image,1)
    # Display the resulting frame
    cv2.imshow('frame', res)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
