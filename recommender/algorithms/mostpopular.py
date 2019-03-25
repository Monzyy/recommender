import numpy as np
import pandas as pd


class MostPopular(object):

    def __init__(self, dataset, train_size=0.8, alpha=0):
        self.dataset = dataset
        self.train_size = 0.8
        self.alpha = alpha

    def compute_popularity(self, ratings=None):
        if ratings is None:
            ratings, _ = self.dataset.get_ratings_split(self.train_size)
        item_r_sum = {}
        total_sum = 0
        count = 0
        for rating in ratings.itertuples():

            item = item_r_sum.get(rating.movie_id, {})
            item['sum'] = item.get('sum', 0) + rating.rating
            item['count'] = item.get('count', 0) + 1
            total_sum += rating.rating
            item_r_sum[rating.movie_id] = item
            count += 1

        overall_avg_rating = total_sum / count
        popularities = []
        for id, item in item_r_sum.items():
            avg_rating = item['sum'] / item['count']
            popularities.append(
                (id, (avg_rating * item['count'] + overall_avg_rating * self.alpha) / (item['count'] + self.alpha)))

        popularities.sort(key=lambda x: x[1], reverse=True)
        return popularities

    def top_n(self, n, ratings=None):
        return self.compute_popularity(ratings)[:n]

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
        popularities = self.compute_popularity()
        for user in rating_df.user_id.unique():
            average_rating = average_rating_df.rating.loc[average_rating_df['user_id'] == user].iloc[0]

            good_recommendations = rating_df.loc[rating_df.user_id == user]
            good_recommendations = good_recommendations[good_recommendations.rating >= average_rating].movie_id

            n_recommendations_needed = good_recommendations.size

            top_n_recommendations = [x[0] for x in popularities[:n_recommendations_needed]]

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
