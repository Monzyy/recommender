import csv
from datetime import datetime

import dateutil
import pandas as pd

from ..database import get_session
from ..models import Movie, Rating

COMMIT_SIZE = 100000


def _load_base(path, model, model_index_mapping):
    def add_instance(line, model_index_mapping, session):
        # Check that all foreign keys references exists, otherwise skip the entry
        for attribute, val in model_index_mapping.items():
            if 'foreign_key_to' in val and not val['parse_func'](line[val['index']]) in val['id_list']:
                return

        # Using model_index_mapping create a dict of (attribute, value) pairs, where the attribute is the
        # models attribute and the value is the parsed value from the input file.
        params = {attribute: val['parse_func'](line[val['index']]) for attribute, val in model_index_mapping.items()}
        session.add(model(**params))

    sess = get_session()

    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Remove header

        i = 0
        for i, line in enumerate(reader):
            try:
                add_instance(line, model_index_mapping, sess)

                if (i + 1) % COMMIT_SIZE == 0:  # Commit every after 100k instances
                    print(f'Commiting {COMMIT_SIZE} instances of {model}. Total committed: {i+1}')
                    sess.commit()
            except (IndexError, ValueError) as e:
                print(e)  # Make sure we see any errors

        sess.commit()
        print(f'Done commiting {i + 1} instances of {model}.')


def load_movies(path):
    # Mapping from Movie attributes to their index and type.
    movies_index_mapping = {
        'id': {
            'index': 0,
            'parse_func': int
        },
        'title': {
            'index': 1,
            'parse_func': str
        },
        'summary': {
            'index': 2,
            'parse_func': str
        },
        'budget': {
            'index': 3,
            'parse_func': int
        },
        'adult': {
            'index': 4,
            'parse_func': _str_to_bool
        },
        'original_language': {
            'index': 5,
            'parse_func': str
        },
        'original_title': {
            'index': 6,
            'parse_func': str
        },
        'poster_path': {
            'index': 7,
            'parse_func': str
        },
        'release_date': {
            'index': 8,
            'parse_func': _str_to_date
        },
        'revenue': {
            'index': 9,
            'parse_func': _float_str_to_int
        },
        'runtime': {
            'index': 10,
            'parse_func': _float_str_to_int
        },
        'status': {
            'index': 11,
            'parse_func': str
        },
        'tagline': {
            'index': 12,
            'parse_func': str
        },
        'video': {
            'index': 13,
            'parse_func': _str_to_bool
        }
    }
    _load_base(path, Movie, movies_index_mapping)


def load_ratings(path):
    # Mapping from Rating attributes to their index and type.
    movie_ids = _get_movie_ids(get_session())
    ratings_index_mapping = {
        'user_id': {
            'index': 0,
            'parse_func': int
        },
        'movie_id': {
            'index': 1,
            'parse_func': int,
            'foreign_key_to': Movie,
            'id_list': movie_ids
        },
        'rating': {
            'index': 2,
            'parse_func': float
        },
        'created_at': {
            'index': 3,
            'parse_func': _unix_timestamp_to_datetime
        }
    }

    _load_base(path, Rating, ratings_index_mapping)


def preprocess_movies(movie_in_path, movie_out_path, link_path):
    # Strip newlines in movies summaries, so each newline corresponds to one item.
    with open(movie_in_path, 'r') as input:
        with open(movie_out_path, 'w') as output:
            output.write(next(input))  # write header
            prev_line = next(input)
            for line in input:
                if line.startswith('False,') or line.startswith('True,'):
                    output.write(prev_line)
                    prev_line = line
                else:
                    # remove newline character at the end of the last line and append the new line
                    prev_line = prev_line[:-1] + line
            output.write(prev_line)  # write last line

    # links to DataFrame
    links = pd.read_csv(link_path)
    links = links[['movieId', 'tmdbId']]
    links = links.dropna()

    # movies to DataFrame
    movies = pd.read_csv(movie_out_path)

    # strip away useless columns
    movies = movies[['id', 'title', 'overview', 'budget', 'adult', 'original_language', 'original_title',
                     'poster_path', 'release_date', 'revenue', 'runtime', 'status', 'tagline', 'video']]

    # merge links and movies
    joined = links.merge(movies, left_on='tmdbId', right_on='id', how='left').drop(['tmdbId', 'id'], axis=1)

    # rename columns
    joined.columns = ['id', 'title', 'summary', 'budget', 'adult', 'original_language', 'original_title',
                      'poster_path', 'release_date', 'revenue', 'runtime', 'status', 'tagline', 'video']

    # set budget to int
    joined.budget = joined.budget.fillna(0).astype(int)

    # remove duplicates
    joined = joined.drop_duplicates('id')

    # write back to disk
    joined.to_csv(movie_out_path, index=False)


def _get_movie_ids(session):
    return [res[0] for res in session.query(Movie.id).all()]


def _str_to_date(string):
    if string:
        return dateutil.parser.parse(string).date()
    return None


def _unix_timestamp_to_datetime(string):
    return datetime.utcfromtimestamp(int(string))


def _float_str_to_int(string):
    if string:
        return int(float(string))
    return None


def _str_to_bool(string):
    return string.lower() == 'true'
