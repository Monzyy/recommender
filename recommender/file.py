if __name__ == '__main__':
    import config
    config.set_settings('LOCAL')
    from algorithms.mostpopular import MostPopular
    mp = MostPopular()
    test = mp.mean_average_precision(mp.ratings_training, mp.user_average_ratings(mp.ratings_training))

    print(test)