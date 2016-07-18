import numpy as np
import scipy


def predict(net, label_colors, image):
    num_classes = len(label_colors)
    image = image.transpose((2, 0, 1))
    net.blobs['data'].data[0] = image
    net.forward()

    predicted = net.blobs['prob'].data
    output = np.squeeze(predicted[0, :, :, :])

    # only use the max-probability non-background class if its probability is
    # above some threshold
    ind = np.argmax(output, axis=0)
    fg = output[:-1, :, :]  # foreground classes only
    bg = np.full(ind.shape, num_classes - 1)
    ind = np.where(np.max(fg, axis=0) > 0.5, ind, bg)

    # construct output image
    r = ind.copy()
    g = ind.copy()
    b = ind.copy()
    a = np.zeros(ind.shape)
    label_colors = np.array(label_colors)
    for l in range(0, num_classes):
        r[ind == l] = label_colors[l, 0]
        g[ind == l] = label_colors[l, 1]
        b[ind == l] = label_colors[l, 2]

    max_prob = np.max(output, axis=0)
    a[ind != num_classes - 1] = max_prob[ind != num_classes - 1] * 255

    rgb = np.zeros((ind.shape[0], ind.shape[1], 4))
    rgb[:, :, 0] = r
    rgb[:, :, 1] = g
    rgb[:, :, 2] = b
    rgb[:, :, 3] = a

    return scipy.misc.toimage(rgb, cmin=0.0, cmax=255, mode='RGBA')
