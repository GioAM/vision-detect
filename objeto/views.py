from django.shortcuts import render
from django.http import HttpResponse
import cv2


def index(request):
    return render(request, 'index.html')




