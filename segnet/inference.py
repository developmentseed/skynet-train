import numpy as np
import scipy


def predict(net, label_colors, image=None):
    num_classes = len(label_colors)

    if image:
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

    max_prob = np.max(output, axis=0)
    return labels_to_image(ind, label_colors, max_prob)


def labels_to_image(labels, label_colors, alpha=None):
    num_classes = len(label_colors)
    # construct output image
    r = labels.copy()
    g = labels.copy()
    b = labels.copy()
    a = np.zeros(labels.shape)
    label_colors = np.array(label_colors)
    for l in range(0, num_classes):
        r[labels == l] = label_colors[l, 0]
        g[labels == l] = label_colors[l, 1]
        b[labels == l] = label_colors[l, 2]

    if (alpha is not None):
        a[labels != num_classes - 1] = alpha[labels != num_classes - 1] * 255
    else:
        a[:] = 255

    rgb = np.zeros((labels.shape[0], labels.shape[1], 4))
    rgb[:, :, 0] = r
    rgb[:, :, 1] = g
    rgb[:, :, 2] = b
    rgb[:, :, 3] = a

    return scipy.misc.toimage(rgb, cmin=0.0, cmax=255, mode='RGBA')
