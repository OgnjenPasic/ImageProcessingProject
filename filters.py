import numpy as np
from PIL import Image
from scipy import signal
import colorsys

# Histogram
def _histogram(slika):
    x = np.array(slika)
    hist1 = [0 for _ in range(256)]
    hist2 = [0 for _ in range(256)]
    hist3 = [0 for _ in range(256)]

    if type(x[0,0]) != np.ndarray:
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                hist1[int(x[i,j])] += 1
        return hist1
    else:
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                hist1[int(x[i,j][0])] += 1
                hist2[int(x[i,j][1])] += 1
                hist3[int(x[i,j][2])] += 1
        return hist1, hist2, hist3
    
def layers(x):
    red_layer = x[:, :, 0]
    green_layer = x[:, :, 1]
    blue_layer = x[:, :, 2]
    return red_layer, green_layer, blue_layer


# Brightness
def brightness_mapping(intensity):
    return np.tan(np.pi * (intensity + 20) / 240) * 3 / 5 + 1 - np.pi / 20

def brightness(image, intensity):
    x = np.array(image)
    mat = np.diag(np.full((x.shape[1],), brightness_mapping(intensity)))
    
    if type(x[0,0]) == np.uint8:
        x = np.dot(x,mat)
        x = np.round(x)
        x[x > 255] = 255
        x[x < 0] = 0
        image = Image.fromarray(np.asarray(x))
        return image
    else:
        red_layer = x[:, :, 0]
        green_layer = x[:, :, 1]
        blue_layer = x[:, :, 2]

        red_layer = np.dot(red_layer, mat)
        red_layer = np.round(red_layer)
        red_layer[red_layer > 255] = 255
        red_layer[red_layer < 0] = 0

        blue_layer = np.dot(blue_layer, mat)
        blue_layer = np.round(blue_layer)
        blue_layer[blue_layer > 255] = 255
        blue_layer[blue_layer < 0] = 0

        green_layer = np.dot(green_layer,mat)
        green_layer = np.round(green_layer)
        green_layer[green_layer > 255] = 255
        green_layer[green_layer < 0] = 0

        x[:, :, 0] = red_layer
        x[:, :, 1] = green_layer
        x[:, :, 2] = blue_layer

        image = Image.fromarray(np.asarray(x))
        return image


# Contrast
def contrast_mapping(x, intensity):
    if intensity < 0:
        k = np.tan(-np.pi * intensity / 220) + 1
        if x <= 128 / k:
            return k * x
        elif x <= (128 + 255 * (k - 1)) / k:
            return 128
        else:
            return k * x - 255 * (k - 1)
    else:
        k = 1 - intensity / 100
        if x < 128:
            return k * x
        else:
            return k * x + (1 - k) * 255

def contrast(image, intensity):
    x = np.array(image)

    if type(x[0,0]) == np.uint8:
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                if contrast_mapping(x[i, j], intensity) == np.nan:
                    x[i, j] = 255
                else:
                    x[i, j] = contrast_mapping(x[i, j], intensity)
        image = Image.fromarray(np.asarray(x))
        return image
    else:
        red_layer = x[:, :, 0]
        green_layer = x[:, :, 1]
        blue_layer = x[:, :, 2]

        for layer in layers(x):
            for i in range(layer.shape[0]):
                for j in range(layer.shape[1]):
                    if contrast_mapping(layer[i, j], intensity) == np.nan:
                        layer[i,j] = 255
                    else:
                        layer[i,j] = contrast_mapping(layer[i,j], intensity)

        x[:, :, 0] = red_layer
        x[:, :, 1] = green_layer
        x[:, :, 2] = blue_layer

        return Image.fromarray(np.asarray(x))


# Rotation
def rotate(image, alpha_degree):
    alpha_radian = np.radians(alpha_degree)
    x = np.array(image)

    if type(x[0,0]) == np.uint8:
        for i in range(x.shape[0]):
            x[i, :] = np.roll(x[i, :], round((i - x.shape[0] / 2) * np.tan(alpha_radian / 2)))
        for i in range(x.shape[1]):
            x[:, i] = np.roll(x[:, i], round((x.shape[1] / 2 - i) * np.sin(alpha_radian)))
        for i in range(x.shape[0]):
            x[i, :] = np.roll(x[i, :], round((i - x.shape[0] / 2) * np.tan(alpha_radian / 2)))
    else:
        red_layer = x[:, :, 0]
        green_layer = x[:, :, 1]
        blue_layer = x[:, :, 2]
        for layer in [red_layer, green_layer, blue_layer]:
            for i in range(layer.shape[0]):
                layer[i, :] = np.roll(layer[i, :], round((i - layer.shape[0] / 2) * np.tan(alpha_radian / 2)))
            for i in range(layer.shape[1]):
                layer[:, i] = np.roll(layer[:, i], round((layer.shape[1] / 2 - i) * np.sin(alpha_radian)))
            for i in range(layer.shape[0]):
                layer[i, :] = np.roll(layer[i, :], round((i - layer.shape[0] / 2) * np.tan(alpha_radian / 2)))

        x[:, :, 0] = red_layer
        x[:, :, 1] = green_layer
        x[:, :, 2] = blue_layer

    output = Image.fromarray(np.asarray(x))
    zoom_intensity = min(x.shape[:1]) / (np.cos(np.abs(alpha_radian)) + np.sin(np.abs(alpha_radian)))
    output = zoom_in(output, zoom_intensity)
    return output


# Median filter
def median_filter(image, filter_size=3):
    x = np.array(image)
    n = filter_size // 2

    for i in range(x.shape[1]):
        for j in range(x.shape[0]):
            lista = []

            for k in range(-n, n + 1):
                for l in range(-n, n + 1):
                    if i + k < 0 or i + k >= x.shape[1]:
                        if j + l < 0 or j + l >= x.shape[0]:
                            lista.append(x[i - k, j - l])
                        else:
                            lista.append(x[i - k, j + l])
                    elif j + l < 0 or j + l > x.shape[0] - 1:
                        lista.append(x[i + k, j - l])
                    else:
                        lista.append(x[i + k, j + l])

            x[i,j] = np.median(lista)

    return Image.fromarray(np.asarray(x))

# Zoom
def zoom_in(image, intensity):
    x = np.array(image)

    if type(x[0,0]) == np.uint8:
        y = np.zeros(x.shape)
        z = np.zeros(x.shape)
        upper_left = int(np.round((x.shape[0] - intensity) / 2))
        ratio = intensity / x.shape[0]
        if intensity <= 10:
            upper_left = int(np.round((x.shape[0] - x.shape[0] / intensity) / 2))
            ratio = 1 / intensity
        for i in range(x.shape[0]):
            y[i] = np.int_(np.round(x[int(np.floor(upper_left + i * ratio))] * (np.floor(i * ratio + 1) - i * ratio)) + x[int(np.floor(upper_left + i * ratio + 1))] * (i * ratio - np.floor(i * ratio)))
        for i in range(y.shape[1]):
           z[:, i] = np.int_(np.round(y[:, int(np.floor(upper_left + i * ratio))] * (np.floor(i * ratio + 1) - i * ratio)) + y[:, int(np.floor(upper_left + i * ratio + 1))] * (i * ratio - np.floor(i * ratio)))

        return Image.fromarray(np.asarray(z))
    else:
        red_layer = x[:, :, 0]
        green_layer = x[:, :, 1]
        blue_layer = x[:, :, 2]

        for layer in [red_layer, green_layer, blue_layer]:
            y = np.zeros(layer.shape)
            upper_left = int(np.round((layer.shape[0] - intensity) / 2))
            ratio = intensity / layer.shape[0]
            if intensity <= 10:
                upper_left = int(np.round((layer.shape[0] - layer.shape[0] / intensity) / 2))
                ratio = 1 / intensity
            for i in range(layer.shape[0]):
                y[i] = np.int_(np.round(layer[int(np.floor(upper_left + i * ratio))] * (np.floor(i * ratio + 1) - i * ratio)) + layer[int(np.floor(upper_left + i * ratio + 1))] * (i * ratio - np.floor(i * ratio)))
            for i in range(y.shape[1]):
                layer[:, i] = np.int_(np.round(y[:, int(np.floor(upper_left + i * ratio))] * (np.floor(i * ratio + 1) - i * ratio)) + y[:, int(np.floor(upper_left + i * ratio + 1))] * (i * ratio - np.floor(i * ratio)))

        x[:, :, 0] = red_layer
        x[:, :, 1] = green_layer
        x[:, :, 2] = blue_layer

        return Image.fromarray(np.asarray(x))

# Shadows & Highlights [shadows - threshold < 128; highlights - threshold > 128]
def shadows_highlights(image, intensity, threshold):
    x = np.array(image)
    y = np.array(brightness(x, intensity))

    if threshold < 128:
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                if np.mean(x[i, j]) < threshold:
                    x[i, j] = y[i, j]
    else:
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                if np.mean(x[i, j]) > threshold :
                    x[i, j] = y[i, j]

    return Image.fromarray(np.asarray(x))


# Linear tilt shift
original = Image.open("lena.tif")
x  = np.array(original)

def linear_tilt_shift(image):
    x = np.array(image)
    h = np.ones((6,6)) / 36

    if type(x[0,0]) == np.uint8:
        x_blurred = x

        for i in range(10):
            x_blurred = signal.convolve(x_blurred, h, 'same')
            x[:int(x.shape[0] / (3 + i))] = x_blurred[:int(x.shape[0] / (3 + i))]
            x[-int(x.shape[0] / (3 + i)):] = x_blurred[-int(x.shape[0] / (3 + i)):]
    else:
        red_layer = x[:, :, 0]
        green_layer = x[:, :, 1]
        blue_layer = x[:, :, 2]

        for layer in [red_layer, green_layer, blue_layer]:
            x_blurred = layer
            for i in range(10):
                x_blurred = signal.convolve(x_blurred, h, 'same')
                layer[:int(layer.shape[0] / (3 + i))] = x_blurred[:int(layer.shape[0] / (3 + i))]
                layer[-int(layer.shape[0] / (3 + i)):] = x_blurred[-int(layer.shape[0] / (3 + i)):]

        x[:, :, 0] = red_layer
        x[:, :, 1] = green_layer
        x[:, :, 2] = blue_layer

    return Image.fromarray(np.asarray(x))


# Radial tilt shift
def distance(i, j, center):
    return np.sqrt((i - center[0]) ** 2 + (j - center[1]) ** 2)

def radial_tilt_shift(image, h =np.ones((5, 5)) / 25):
    x = np.array(image)

    if type(x[0,0]) == np.uint8:
        center = [x.shape[0] / 2, x.shape[1] / 2]
        x_blurred = x

        for k in range(5):
            x_blurred = signal.convolve(x_blurred, h, 'same')
            for i in range(x.shape[0]):
                for j in range(x.shape[1]):
                    if distance(i, j, center) > distance(0,0, center) / 3 + (2 * distance(0, 0, center) / 15) * k:
                        x[i, j] = x_blurred[i, j]
    else:
        red_layer = x[:, :, 0]
        green_layer = x[:, :, 1]
        blue_layer = x[:, :, 2]

        for layer in [red_layer, green_layer, blue_layer]:
            center = [layer.shape[0] / 2, layer.shape[1] / 2]
            x_blurred = layer
            for k in range(5):
                x_blurred = signal.convolve(x_blurred, h, 'same')
                for i in range(layer.shape[0]):
                    for j in range(layer.shape[1]):
                        if distance(i, j, center) > distance(0, 0, center) / 3 + (2 * distance(0, 0, center) / 15) * k:
                            layer[i, j] = x_blurred[i, j]

        x[:, :, 0] = red_layer
        x[:, :, 1] = green_layer
        x[:, :, 2] = blue_layer

    return Image.fromarray(np.asarray(x))


# Vignette
def distance(i, j, center):
    return np.sqrt((i - center[0]) ** 2 + (j - center[1]) ** 2)

def vignette(image):
    x = np.array(image)

    if type(x[0,0]) == np.uint8:
        center = [x.shape[0] / 2, x.shape[1] / 2]
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                if x[i, j] - (distance(i, j, center) ** 2) / 350 > 0:
                    x[i, j] = int(x[i, j] - (distance(i, j, center) ** 2) / 350)
                else:
                    x[i, j] = 0
    else:
        red_layer = x[:, :, 0]
        green_layer = x[:, :, 1]
        blue_layer = x[:, :, 2]

        center = [red_layer.shape[0] / 2, red_layer.shape[1] / 2]
        for layer in layers(x):
            for i in range(layer.shape[0]):
                for j in range(layer.shape[1]):
                    if layer[i, j] - (distance(i, j, center) ** 2) / 350 > 0:
                        layer[i, j] = int(layer[i, j] - (distance(i, j, center) ** 2) / 350)
                    else:
                        layer[i, j] = 0

        x[:, :, 0] = red_layer
        x[:, :, 1] = green_layer
        x[:, :, 2] = blue_layer

    return Image.fromarray(np.asarray(x))


# Warmth
def warmth(image, intensity):
    x = np.array(image)
    x_p = x.copy()

    for i in range(x_p.shape[1]):
        for j in range(x_p.shape[0]):
            r, g, b = x_p[i, j]

            if r + intensity > 255:
                r_p = 255
            elif r + intensity < 0:
                r_p = 0
            else:
                r_p = r + intensity

            if b - intensity > 255:
                b_p = 255
            elif b - intensity < 0:
                b_p = 0
            else:
                b_p = b - intensity

            x_p[i, j] = [r_p, g, b_p]

    return Image.fromarray(np.asarray(x_p))

# Saturation
def saturation(image, intensity):
    x = np.array(image)
    x_p = x.copy()

    for i in range(x_p.shape[0]):
        for j in range(x_p.shape[1]):
            r, g, b = x_p[i, j]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            s_p = s + (1 - s) * intensity / 100
            if s_p < 0:
                s_p = 0

            x_p[i, j] = colorsys.hsv_to_rgb(h, s_p, v)

    return Image.fromarray(np.asarray(x_p))


# Fade (washed out)
def fade_washed(image, intensity):
    x = np.array(image)
    x_p = x.copy()
    x_w_o = shadows_highlights(image, 20, 100)
    x_n = np.array(saturation(x_w_o, -50))

    for i in range(x_p.shape[1]):
        for j in range(x_p.shape[0]):
            r_p, g_p, b_p = x_p[i, j]
            r_n, g_n, b_n = x_n[i, j]
            r_f = (100 - intensity) / 100 * r_p + intensity / 100 * r_n
            g_f = (100 - intensity) / 100 * g_p + intensity / 100 * g_n
            b_f = (100 - intensity) / 100 * b_p + intensity / 100 * b_n

            x_p[i, j] = [r_f, g_f, b_f]

    return Image.fromarray(np.asarray(x_p))

# Fade (white)
def fade_white(image, intensity):
    x = np.array(image)
    x_p = x.copy()
    x_n = np.zeros([512, 512, 3], dtype=np.uint8)
    x_n.fill(255)

    for i in range(x_p.shape[1]):
        for j in range(x_p.shape[0]):
            r_p, g_p, b_p = x_p[i, j]
            r_n, g_n, b_n = x_n[i, j]
            r_f = (100 - intensity) / 100 * r_p + intensity / 100 * r_n
            g_f = (100 - intensity) / 100 * g_p + intensity / 100 * g_n
            b_f = (100 - intensity) / 100 * b_p + intensity / 100 * b_n

            x_p[i, j] = [r_f, g_f, b_f]

    return Image.fromarray(np.asarray(x_p))


# Sharpen
def sharpen(image):
    x = np.array(image)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

    if type(x[0,0]) != np.uint8:
        red_layer = x[:, :, 0]
        green_layer = x[:, :, 1]
        blue_layer = x[:, :, 2]

        l_red_layer = signal.convolve2d(red_layer, kernel, 'same')
        l_green_layer = signal.convolve2d(green_layer, kernel, 'same')
        l_blue_layer = signal.convolve2d(blue_layer, kernel, 'same')
        y = x
        y[:, :, 0] = standard(l_red_layer)
        y[:, :, 1] = standard(l_green_layer)
        y[:, :, 2] = standard(l_blue_layer)
    else:
        x = signal.convolve2d(x, kernel, 'same')
        y = standard(x)
    return Image.fromarray(np.asarray(y))

def standard(mat):
    mat[mat > 255] = 255
    mat[mat < 0] = 0
    return mat.astype(np.uint8)