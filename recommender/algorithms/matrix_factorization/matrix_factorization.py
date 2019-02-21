import numpy as np


class MatrixFactorization: # TODO: it needs to be stochastic, or at least kinda

    def fit(self, ratings: np.ndarray, n_latent_factors: int, steps=5000, alpha=0.0002, beta=0.02):

        n_users, n_items = ratings.shape

        P = np.random.rand(n_users, n_latent_factors)
        Q = np.random.rand(n_latent_factors, n_items)

        for i in range(0, steps):
            pred = self._compute_prediction(P, Q)
            error = self._compute_error(ratings, pred)
            grad_p, grad_q = self._compute_gradients(error, P, Q, beta)

            # Update
            P = P+alpha*grad_p
            Q = Q+alpha*grad_q

            if error < 0.001:
                break

        return P, Q

    def _compute_gradients(self, error, P, Q, beta):
        delta_p = 2*error*P-beta*Q
        delta_q = 2*error*Q-beta*P

        return delta_p, delta_q

    def _compute_prediction(self, P, Q):
        return np.dot(P, Q)

    def _compute_error(self, ratings, pred):
        return np.square(ratings-pred).mean()


if __name__ == "__main__":
    print("yay")

    ratings = np.array([[5, 4, 0, 1],
                        [4, 0, 0, 1],
                        [1, 1, 0, 5],
                        [1, 0, 0, 4],
                        [0, 1, 5, 4]
                        ])

    mat_fac = MatrixFactorization()

    p, q = mat_fac.fit(ratings, 2)

    print(np.dot(p, q))
