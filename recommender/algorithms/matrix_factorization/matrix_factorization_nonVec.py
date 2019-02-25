import numpy as np

class MatrixFactorization: # TODO: it needs to be stochastic, or at least kinda

    def fit(self, ratings: np.ndarray, n_latent_factors: int, steps=10000, alpha=0.0002, beta=0.02):

        n_users, n_items = ratings.shape

        P = np.random.rand(n_users, n_latent_factors)
        Q = np.random.rand(n_latent_factors, n_items)

        
        for step in range(0, steps):
            pred = self._compute_prediction(P, Q)
            error = self._compute_error(ratings, pred)
            reg_error = 0
            breaker = []
            for u in range(0, n_users):
                for i in range (0, n_items):
                    if ratings[u, i] > 0:
                        e = error[u, i]
                        P[u] = P[u] + alpha * (2 * e * Q[:, i] - beta*P[u])
                        Q[:, i] = Q[:, i] + alpha*(2 * e * P[u] - beta*Q[:, i]) 

                        reg_error += np.square(e) + beta * (np.square(np.linalg.norm(P[u])) + np.square(np.linalg.norm(Q[:, i])))
                        breaker.append(e)
            
            if step % 100 == 0:
                print("{0}: {1}".format(step, reg_error))
            if np.mean(breaker) < 0.001:
                print("BREAK")
                break

        return P, Q

    def _compute_prediction(self, P, Q):
        return np.dot(P, Q)

    def _compute_error(self, ratings, pred):
        return ratings-pred


if __name__ == "__main__":
    print("yay")

    ratings = np.array([[5, 4, 0, 1],
                        [4, 0, 0, 1],
                        [1, 1, 0, 5],
                        [1, 0, 0, 4],
                        [0, 1, 5, 4]
                        ])

    mat_fac = MatrixFactorization()

    p, q = mat_fac.fit(ratings, 3)

    print(np.dot(p, q))
