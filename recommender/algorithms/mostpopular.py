from .common import Recommender


class MostPopular(Recommender):
    _popularities = []  # list for storing recommendation so they don't have to be recomputed.

    def __init__(self, dataset, train_size=0.8, alpha=0):
        Recommender.__init__(self, dataset, train_size)
        self.alpha = alpha

    def compute_popularity(self, ratings=None, recompute=False):
        if self._popularities and not recompute:
            return self._popularities
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
        self._popularities = popularities
        return popularities

    def top_n(self, n, user=None, ratings=None):
        return self.compute_popularity(ratings)[:n]
