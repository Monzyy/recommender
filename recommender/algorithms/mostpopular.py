import pandas as pd

from ratings.database import engine, get_session
from ratings.models import Rating


class MostPopular(object):

    def __init__(self):
        connection = engine.connect()
        self.items = pd.read_sql_table('movies', connection)
        self.items = self.items.rename(columns={'id': 'movie_id'})
        ratings = pd.read_sql_table('ratings', connection)
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
        alpha = 100
        popularities = []
        for id, item in item_r_sum.items():
            avg_rating = item['sum'] / item['count']
            popularities.append((id,
                                (avg_rating * item['count'] + overall_avg_rating * alpha) / (item['count'] + alpha)))

        popularities.sort(key=lambda x: x[1], reverse=True)
        return popularities

    def top_10(self):
        popularities = self.compute_popularity()
        for pop in popularities[:10]:
            print(self.items.loc[self.items['movie_id'] == pop[0]].title)
