import cv2
import numpy as np

def sobel_edges(channel):
    ch = channel.astype(np.float64)
    grad_x = cv2.Sobel(ch, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(ch, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.hypot(grad_x, grad_y)
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def laplacian_edges(channel):
    ch = channel.astype(np.float64)
    lap = cv2.Laplacian(ch, cv2.CV_64F)
    return cv2.convertScaleAbs(lap)

def scharr_edges(channel):
    ch = channel.astype(np.float64)
    grad_x = cv2.Scharr(ch, cv2.CV_64F, 1, 0)
    grad_y = cv2.Scharr(ch, cv2.CV_64F, 0, 1)
    magnitude = np.hypot(grad_x, grad_y)
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
