import numpy as np
import pandas as pd


class Recommender(object):
    def __init__(self, dataset, train_size):
        self.dataset = dataset
        self.train_size = 0.8

    def top_n(self, n, user=None):
        return NotImplementedError('This method must be implemented in subclasses')

    def user_average_ratings(self, dataframe):
        user_average_ratings = pd.DataFrame(data=None, columns=['user_id', 'rating'])

        for id in dataframe.user_id.unique():
            elements = dataframe[dataframe.user_id == id].rating
            size = elements.shape[0]
            ratings_total = elements.values.sum()
            user_average_ratings = user_average_ratings.append(
                pd.Series([id, (ratings_total / size)], index=user_average_ratings.columns), ignore_index=True)

        return user_average_ratings

    def mean_average_precision(self, rating_df, average_rating_df):
        list_of_ap = []
        for user in rating_df.user_id.unique():
            average_rating = average_rating_df.rating.loc[average_rating_df['user_id'] == user].iloc[0]

            good_recommendations = rating_df.loc[rating_df.user_id == user]
            good_recommendations = good_recommendations[good_recommendations.rating >= average_rating].movie_id

            n_recommendations_needed = good_recommendations.size

            top_n_recommendations = [x[0] for x in self.top_n(n=n_recommendations_needed, user=user)]

            total_recs = 0
            correct_recs = 0
            scorelist = []
            for rec in top_n_recommendations:
                total_recs += 1
                if rec in good_recommendations:
                    scorelist.append(1/total_recs)
                    correct_recs += 1

            if correct_recs != 0:
                score = sum(scorelist)/correct_recs
            else:
                score = 0

            list_of_ap.append(score)

        return np.mean(list_of_ap)