import numpy as np
from scipy.signal import fftconvolve
from scipy.signal.windows import gaussian
from scipy.sparse.linalg import LinearOperator


def get_l2norm(A, n_iter=100):
    # multiplication for the smaller size of matrice
    if A.shape[0] < A.shape[1]:
        A = A.T
    AtA = A.T @ A
    x = np.random.randn(A.shape[1], A.shape[1])
    for _ in range(n_iter):
        x = AtA @ x
        x /= np.linalg.norm(x)
    return np.sqrt(np.linalg.norm(AtA @ x))


def make_blur(type_A, height, size=27, std=8):
    if type_A == 'denoising':
        A = LinearOperator(
            dtype=np.float64,
            matvec=lambda x: x,
            matmat=lambda X: X,
            rmatvec=lambda x: x,
            rmatmat=lambda X: X,
            shape=(height, height),
        )
    elif type_A == 'deblurring':
        filt = np.outer(
            gaussian(size, std),
            gaussian(size, std))
        filt /= filt.sum()
        A = LinearOperator(
            dtype=np.float64,
            matvec=lambda x: fftconvolve(x, filt, mode='same'),
            matmat=lambda X: fftconvolve(X, filt, mode='same'),
            rmatvec=lambda x: fftconvolve(x, filt, mode='same'),
            rmatmat=lambda X: fftconvolve(X, filt, mode='same'),
            shape=(height, height),
        )
    return A


def huber(R, delta):
    norm_1 = np.abs(R)
    loss = np.where(norm_1 < delta,
                    0.5 * norm_1**2,
                    delta * norm_1 - 0.5 * delta**2)
    return np.sum(loss)


def grad_huber(R, delta):
    return np.where(np.abs(R) < delta, R,
                    np.sign(R) * delta)


def grad_F(y, A, u, data_fit, delta):
    R = A @ u - y
    if data_fit == 'lsq':
        return A.T @ R
    elif data_fit == 'huber':
        return A.T @ grad_huber(R, delta)
