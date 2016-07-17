import numpy as np


# + + + + + + + + + + + + + + + + +
# + + + + + + + + + + + + + + + + +
# + + + + + + + + + + + + + + + + +
# + + + @ + + + + + + + + + + + + +
# + + + + + + + + + + + + + + + + +
# + + + + + + + + + + + + + + + + +
# + + + + + + + + + + + + + + + + +
def complete_and_correct(output, label, r, threshold):
    num_classes = output.shape[0]
    bg = num_classes - 1
    predicted_pixels = np.zeros((num_classes,))
    actual_pixels = np.zeros((num_classes,))

    # only use the max-probability non-background class if its probability is
    # above the threshold
    ind = np.argmax(output, axis=0)
    fg = output[:-1, :, :]  # foreground classes only
    prediction = np.where(np.max(fg, axis=0) > threshold, ind, num_classes - 1)

    # for each class, the number of pixels where that class is predicted and
    # the groundtruth includes a pixel with that class within r pixels.
    # (i.e., number of true positives)
    correct = np.zeros((num_classes - 1,))

    # for each class, the number of pixels where that class is the true value
    # and the predicted output includes a pixel with that class within r pixels
    # (i.e., actual_pixels - number of false negatives)
    complete = np.zeros((num_classes - 1,))

    # todo -- deal with image boundaries
    for x in range(r + 1, label.shape[0] - r - 1):
        for y in range(r + 1, label.shape[1] - r - 1):
            # assess completeness contribution of this pixel
            a_class = label[x, y]
            p_win = prediction[x - r: x + r, y - r: y + r]
            actual_pixels[a_class] += 1
            if a_class != bg and (p_win == a_class).any():
                complete[a_class] += 1
            # assess correctness contribution of this pixel
            p_class = prediction[x, y]
            a_win = label[x - r: x + r, y - r: y + r]
            predicted_pixels[p_class] += 1
            if p_class != bg and (a_win == p_class).any():
                    correct[p_class] += 1

    return {
        'pixels_correct': correct.tolist(),
        'pixels_predicted': predicted_pixels.tolist(),
        'pixels_actual': actual_pixels.tolist(),
        'pixels_complete': complete.tolist(),
        'completeness_score': np.sum(complete) / np.sum(actual_pixels[:-1]),
        'correctness_score': np.sum(correct) / np.sum(predicted_pixels[:-1])
    }
