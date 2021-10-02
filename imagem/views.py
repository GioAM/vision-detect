from django.shortcuts import render
from django.http import HttpResponse
import cv2


def camera(request):
    return render(request, 'camera.html')


def rodar_camera(request):
    video = cv2.VideoCapture(0)
    while True:
        ret, frame = video.read()
        cv2.imshow("Image", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    video.release()
    cv2.destroyAllWindows()
