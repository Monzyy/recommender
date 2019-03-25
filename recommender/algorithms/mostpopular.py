import pandas as pd
import numpy as np

from ratings.database import engine, get_session
from ratings.models import Rating


class MostPopular(object):

    def __init__(self):
        connection = engine.connect()
        self.items = pd.read_sql_table('movies', connection, schema="main")
        self.items = self.items.rename(columns={'id': 'movie_id'})
        ratings = pd.read_sql_table('ratings', connection, schema="main")
        users = ratings.user_id.unique()
        user_cutoff = int(len(users) * 0.8)
        self.user_training = users[:user_cutoff]
        self.user_testing = users[user_cutoff:]
        self.ratings_training = ratings[ratings.user_id.isin(self.user_training)]
        self.ratings_testing = ratings[ratings.user_id.isin(self.user_testing)]

    def split(self):
        return self._split_data_base()

    def _split_data_base(self):
        session = get_session()
        count = session.query(Rating).count()
        all = get_session().query(Rating).order_by(Rating.created_at).all()
        cutoff = int(count * 0.8)
        return all[:cutoff], all[cutoff:]

    def compute_popularity(self):
        item_r_sum = {}
        total_sum = 0
        count = 0
        for rating in self.ratings_training.itertuples():

            item = item_r_sum.get(rating.movie_id, {})
            item['sum'] = item.get('sum', 0) + rating.rating
            item['count'] = item.get('count', 0) + 1
            total_sum += rating.rating
            item_r_sum[rating.movie_id] = item
            count += 1

        overall_avg_rating = total_sum / count
        alpha = 1000
        popularities = []
        for id, item in item_r_sum.items():
            avg_rating = item['sum'] / item['count']
            popularities.append((id,
                                (avg_rating * item['count'] + overall_avg_rating * alpha) / (item['count'] + alpha)))

        popularities.sort(key=lambda x: x[1], reverse=True)
        return popularities

    def top_n(self, n):
        popularities = self.compute_popularity()
        return popularities[:n]


    def user_average_ratings(self, dataframe):
        user_average_ratings = pd.DataFrame(data=None, columns=['user_id', 'rating'])

        for id in dataframe.user_id.unique():
            elements = dataframe[dataframe.user_id == id].rating
            size = elements.shape[0]
            ratings_total = elements.values.sum()
            user_average_ratings = user_average_ratings.append(pd.Series([id, (ratings_total / size)], index=user_average_ratings.columns), ignore_index=True)

        return user_average_ratings

    def mean_average_precision(self, rating_df, average_rating_df):
        list_of_ap = []
        for user in rating_df.user_id.unique():
            average_rating = average_rating_df.rating.loc[average_rating_df['user_id'] == user].iloc[0]

            good_recommendations = rating_df.loc[rating_df.user_id == user]
            good_recommendations = good_recommendations[good_recommendations.rating >= average_rating].movie_id

            n_recommendations_needed = good_recommendations.size

            top_n_recommendations = MostPopular.top_n(self, n=n_recommendations_needed)
            top_n_recommendations = [x[0] for x in top_n_recommendations]

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


