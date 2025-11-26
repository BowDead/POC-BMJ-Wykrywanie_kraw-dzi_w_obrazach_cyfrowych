import cv2
import numpy as np
from scipy.ndimage import gaussian_filter

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

def canny_cv2_edges(channel, low_t=50, high_t=150):
    ch = channel.astype(np.uint8)
    edges = cv2.Canny(ch, low_t, high_t)
    return edges


def canny_edges(channel, low_t=0, high_t=255):
    """
    Soft Canny edges using explicit Sobel kernels with non-maximum suppression.
    Returns uint8 edges clipped to [low_t, high_t].
    """
    import numpy as np
    import cv2

    ch = channel.astype(np.float64)
    blurred = cv2.GaussianBlur(ch, (5, 5), 1.4)

    # Sobel kernels
    sobel_x = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]], dtype=np.float64)
    sobel_y = np.array([[-1, -2, -1],
                        [ 0,  0,  0],
                        [ 1,  2,  1]], dtype=np.float64)

    # Gradients using convolution
    Ix = fast_convolve2d(blurred, sobel_x)
    Iy = fast_convolve2d(blurred, sobel_y)

    mag = np.hypot(Ix, Iy)
    angle = np.arctan2(Iy, Ix)

    # Non-maximum suppression
    M, N = mag.shape
    nms = np.zeros((M, N), dtype=np.float64)
    angle_deg = angle * 180. / np.pi
    angle_deg[angle_deg < 0] += 180

    for i in range(1, M-1):
        for j in range(1, N-1):
            a = angle_deg[i, j]
            try:
                if (0 <= a < 22.5) or (157.5 <= a <= 180):
                    q = mag[i, j+1]; r = mag[i, j-1]
                elif 22.5 <= a < 67.5:
                    q = mag[i+1, j-1]; r = mag[i-1, j+1]
                elif 67.5 <= a < 112.5:
                    q = mag[i+1, j]; r = mag[i-1, j]
                elif 112.5 <= a < 157.5:
                    q = mag[i-1, j-1]; r = mag[i+1, j+1]

                if mag[i, j] >= q and mag[i, j] >= r:
                    nms[i, j] = mag[i, j]
            except IndexError:
                pass

    # Clip to user-defined range
    nms = np.clip(nms, low_t, high_t)

    # Normalize to 0-255
    nms = cv2.normalize(nms, None, 0, 255, cv2.NORM_MINMAX)

    return nms.astype(np.uint8)

def roberts_edges(channel, low_t=0, high_t=255):
    """Edge detection using Roberts cross operator (2x2) without cv2."""
    # Roberts cross kernels (2x2)
    roberts_x = np.array([[1, 0],
                          [0, -1]], dtype=np.float64)
    roberts_y = np.array([[0, 1],
                          [-1, 0]], dtype=np.float64)

    # ensure float for convolution
    grad_x = fast_convolve2d(channel, roberts_x)
    grad_y = fast_convolve2d(channel, roberts_y)

    magnitude = np.hypot(grad_x, grad_y)
    magnitude = np.clip(magnitude, low_t, high_t)

    # normalize to 0-255 uint8 like other functions
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)