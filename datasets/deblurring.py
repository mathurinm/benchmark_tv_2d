from benchopt import BaseDataset
from benchopt import safe_import_context

with safe_import_context() as import_ctx:
    import numpy as np
    from scipy import misc
    from benchmark_utils.shared import make_blur


class Dataset(BaseDataset):

    name = "Deblurring"

    # List of parameters to generate the datasets. The benchmark will consider
    # the cross product for each key in the dictionary.
    parameters = {
        'std_noise': [0.02],
        'size_blur': [27],
        'std_blur': [2.],
        'subsampling': [4],
        'type_A': ['deblurring'],
        'type_n': ['gaussian', 'laplace']
    }

    def __init__(self, std_noise=0.3,
                 size_blur=27, std_blur=8.,
                 subsampling=4,
                 random_state=27,
                 type_A='deblurring',
                 type_n='gaussian'):
        self.std_noise = std_noise
        self.size_blur = size_blur
        self.std_blur = std_blur
        self.subsampling = subsampling
        self.random_state = random_state
        self.type_A, self.type_n = type_A, type_n

    def set_A(self, height):
        return make_blur(self.type_A, height,
                         self.size_blur, self.std_blur)

    def get_data(self):
        rng = np.random.RandomState(self.random_state)
        img = misc.face(gray=True)[::self.subsampling, ::self.subsampling]
        img = img / 255.0
        height, width = img.shape
        if self.type_n == 'gaussian':
            n = rng.normal(0, self.std_noise, size=(height, width))
        elif self.type_n == 'laplace':
            n = rng.laplace(0, self.std_noise, size=(height, width))
        A = self.set_A(height)
        y_degraded = A @ img + n

        return dict(A=A, y=y_degraded)
