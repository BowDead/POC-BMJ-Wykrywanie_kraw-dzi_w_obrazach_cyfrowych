import cv2
import numpy as np

def fast_convolve2d(image, kernel):
    """Performs a fast 2D convolution using numpy's stride tricks."""
    image = image.astype(np.float64)
    kernel = np.flipud(np.fliplr(kernel))
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2
    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='reflect')

    # generate shifted windows
    shape = (image.shape[0], image.shape[1], kh, kw)
    strides = padded.strides * 2
    windows = np.lib.stride_tricks.as_strided(padded, shape=shape, strides=strides)

    # calculate convolution vectorially
    return np.tensordot(windows, kernel, axes=((2, 3), (0, 1)))


def sobel_edges_old(channel):
    """Edge detection using cv2.Sobel (for comparison/legacy)."""
    ch = channel.astype(np.float64)
    grad_x = cv2.Sobel(ch, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(ch, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.hypot(grad_x, grad_y)
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def sobel_edges(channel, low_t=0, high_t=255):
    """Edge detection using Sobel filter without cv2.Sobel."""
    sobel_x = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]], dtype=np.float64)

    sobel_y = np.array([[-1, -2, -1],
                        [ 0,  0,  0],
                        [ 1,  2,  1]], dtype=np.float64)

    grad_x = fast_convolve2d(channel, sobel_x)
    grad_y = fast_convolve2d(channel, sobel_y)
    magnitude = np.hypot(grad_x, grad_y)
    magnitude = np.clip(magnitude, low_t, high_t)
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def laplacian_edges(channel, low_t=0, high_t=255):
    """Edge detection using Laplacian filter without cv2.Laplacian."""
    laplacian_kernel = np.array([[0,  1, 0],
                                 [1, -4, 1],
                                 [0,  1, 0]], dtype=np.float64)

    lap = fast_convolve2d(channel, laplacian_kernel)
    lap = np.clip(lap, low_t, high_t)

    return cv2.convertScaleAbs(lap)


def scharr_edges(channel, low_t=0, high_t=255):
    """Edge detection using Scharr filter without cv2.Scharr."""
    scharr_x = np.array([[-3, 0, 3],
                         [-10, 0, 10],
                         [-3, 0, 3]], dtype=np.float64)

    scharr_y = np.array([[-3, -10, -3],
                         [ 0,   0,  0],
                         [ 3,  10,  3]], dtype=np.float64)

    grad_x = fast_convolve2d(channel, scharr_x)
    grad_y = fast_convolve2d(channel, scharr_y)
    magnitude = np.hypot(grad_x, grad_y)
    magnitude = np.clip(magnitude, low_t, high_t)
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

def prewitt_edges(channel, low_t=0, high_t=255):
    """Edge detection using Prewitt filter."""
    prewitt_x = np.array([[-1, 0, 1],
                          [-1, 0, 1],
                          [-1, 0, 1]], dtype=np.float64)

    prewitt_y = np.array([[1, 1, 1],
                          [0, 0, 0],
                          [-1, -1, -1]], dtype=np.float64)

    grad_x = fast_convolve2d(channel, prewitt_x)
    grad_y = fast_convolve2d(channel, prewitt_y)
    magnitude = np.hypot(grad_x, grad_y)
    magnitude = np.clip(magnitude, low_t, high_t)
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)