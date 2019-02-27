import numpy as np
import pandas as pd
import datetime

class MatrixFactorization: # TODO: it needs to be stochastic, or at least kinda

    def fit(self, ratings, n_users, n_items, n_latent_factors: int, steps=10000, alpha=0.0002, beta=0.02):
        P = np.random.rand(n_users, n_latent_factors)
        Q = np.random.rand(n_latent_factors, n_items)

        print("Started fitting of model at time: {0}...".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        for step in range(0, steps):
            #pred = self._compute_prediction(P, Q)
            #error = self._compute_error(ratings, pred)
            reg_error = 0
            breaker = []
            for index, row in ratings.iterrows(): # ["userId", "movieId", "rating", "timestamp"]
                user = row["userId"].astype(np.int32) - 1
                item = row["movieId"].astype(np.int32) - 1
                rating = row["rating"]

                error = rating - np.dot(P[user], Q[:, item])
                P[user] = P[user] + alpha * (2 * error * Q[:, item] - beta * P[user])
                Q[:, item] = Q[:, item] + alpha*(2 * error * P[user] - beta * Q[:, item])

                if step % 100 == 0:
                    reg_error += \
                        np.square(error) + \
                        beta * (np.square(np.linalg.norm(P[user])) + np.square(np.linalg.norm(Q[:, item])))
                breaker.append(error)

                # for u in range(0, n_users):
                #     for i in range (0, n_items):
                #         if ratings[u, i] > 0:
                #             e = error[u, i]
                #             P[u] = P[u] + alpha * (2 * e * Q[:, i] - beta*P[u])
                #             Q[:, i] = Q[:, i] + alpha*(2 * e * P[u] - beta*Q[:, i])


            if step % 100 == 0:
                print("done with step {0} at time {1}. Error: {2}".format(step, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), reg_error))
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
    ratings = pd.read_csv("../../the-movies-dataset/ratings_small.csv")
    print("Done reading file...")
    n_users = ratings["userId"].unique().max()
    n_items = ratings["movieId"].unique().max()

    mat_fac = MatrixFactorization()
    p, q = mat_fac.fit(ratings, n_users=n_users, n_items=n_items, n_latent_factors=3)


    print("Saving P and Q to .npy files")
    np.save("p", p)
    np.save("q", q)


