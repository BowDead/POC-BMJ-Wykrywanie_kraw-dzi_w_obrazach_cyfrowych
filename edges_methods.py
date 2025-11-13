import cv2
import numpy as np

def fast_convolve2d(image, kernel):
    image = image.astype(np.float64)
    kernel = np.flipud(np.fliplr(kernel))
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2
    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='reflect')

    # generowanie przesuniętych okien
    shape = (image.shape[0], image.shape[1], kh, kw)
    strides = padded.strides * 2
    windows = np.lib.stride_tricks.as_strided(padded, shape=shape, strides=strides)

    # obliczenie konwolucji wektorowo
    return np.tensordot(windows, kernel, axes=((2, 3), (0, 1)))


def sobel_edges_old(channel):
    ch = channel.astype(np.float64)
    grad_x = cv2.Sobel(ch, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(ch, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.hypot(grad_x, grad_y)
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def sobel_edges(channel):
    """Detekcja krawędzi filtrem Sobela bez użycia cv2.Sobel."""
    sobel_x = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]], dtype=np.float64)

    sobel_y = np.array([[-1, -2, -1],
                        [ 0,  0,  0],
                        [ 1,  2,  1]], dtype=np.float64)

    grad_x = fast_convolve2d(channel, sobel_x)
    grad_y = fast_convolve2d(channel, sobel_y)
    magnitude = np.hypot(grad_x, grad_y)

    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def laplacian_edges(channel):
    """Detekcja krawędzi filtrem Laplace’a bez użycia cv2.Laplacian."""
    laplacian_kernel = np.array([[0,  1, 0],
                                 [1, -4, 1],
                                 [0,  1, 0]], dtype=np.float64)

    lap = fast_convolve2d(channel, laplacian_kernel)
    return cv2.convertScaleAbs(lap)


def scharr_edges(channel):
    """Detekcja krawędzi filtrem Scharra bez użycia cv2.Scharr."""
    scharr_x = np.array([[-3, 0, 3],
                         [-10, 0, 10],
                         [-3, 0, 3]], dtype=np.float64)

    scharr_y = np.array([[-3, -10, -3],
                         [ 0,   0,  0],
                         [ 3,  10,  3]], dtype=np.float64)

    grad_x = fast_convolve2d(channel, scharr_x)
    grad_y = fast_convolve2d(channel, scharr_y)
    magnitude = np.hypot(grad_x, grad_y)

    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
