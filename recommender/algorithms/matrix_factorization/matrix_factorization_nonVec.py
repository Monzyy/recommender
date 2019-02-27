import numpy as np
import pandas as pd
import datetime

class MatrixFactorization: # TODO: it needs to be stochastic, or at least kinda

    def fit(self, ratings, n_users, n_items, n_latent_factors: int, steps=10000, alpha=0.0002, beta=0.02):
        P = np.random.rand(n_users, n_latent_factors)
        Q = np.random.rand(n_latent_factors, n_items)

        print("Started fitting of model at time: {0}...".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        for step in range(0, steps):
            reg_error = 0
            breaker = []
            for row in ratings.itertuples(index=False, name='row'): # ["userId", "movieId", "rating", "timestamp"]
                user = row.userId - 1
                item = row.movieId - 1
                rating = row.rating

                p_u = P[user]
                q_i = Q[:, item]
                error = rating - np.dot(p_u, q_i)
                P[user] = p_u + alpha * (2 * error * q_i - beta * p_u)
                Q[:, item] = q_i + alpha*(2 * error * p_u - beta * q_i)

                if step % 100 == 0:
                    reg_error += \
                        np.square(error) + \
                        beta * (np.square(np.linalg.norm(p_u) + np.square(np.linalg.norm(q_i))))
                breaker.append(error)

            if step % 100 == 0:
                print("done with step: {0} at time {1}. Error: {2}".format(step, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), reg_error))
            else:
                print("done with step: {0} at time {1}".format(step, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            if np.mean(breaker) < 0.001:
                print("BREAK")
                break
        print("Done fitting model...")
        return P, Q

    def _compute_prediction(self, P, Q):
        return np.dot(P, Q)

    def _compute_error(self, ratings, pred):
        return ratings-pred


if __name__ == "__main__":
    print("Started reading file...")
    ratings = pd.read_csv("../../the-movies-dataset/ratings_small.csv",
                          usecols=['userId', 'movieId' , 'rating'])
    print("Done reading file...")
    n_users = ratings["userId"].unique().max()
    n_items = ratings["movieId"].unique().max()

    mat_fac = MatrixFactorization()
    p, q = mat_fac.fit(ratings, n_users=n_users, n_items=n_items, n_latent_factors=3)


    print("Saving P and Q to .npy files")
    np.save("p", p)
    np.save("q", q)


