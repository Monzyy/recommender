if __name__ == '__main__':
    import config
    config.set_settings('LOCAL')
    from algorithms.mostpopular import MostPopular
    from dataset.movielens import MovieLensDS
    mlds = MovieLensDS(l_from='db', use_ml_1m=False)
    mp = MostPopular(mlds)
    ratings_training, ratings_testing = mp.dataset.get_ratings_split()
    test = mp.mean_average_precision(ratings_testing, mp.user_average_ratings(ratings_testing))

    print(test)
