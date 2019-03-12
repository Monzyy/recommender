import csv
import json
from datetime import datetime

import dateutil

from ..database import get_session
from ..models import (Genre, Movie, ProductionCompany, ProductionCountry,
                      Rating, SpokenLanguage)

COMMIT_SIZE = 100000
ASSOCIATION_CACHE = {'genres': {}, 'production_companies': {}, 'production_countries': {}, 'spoken_languages': {}}
COUNTRY_IDS = {}
SPOKEN_LANGUAGE_IDS = {}


def _load_base(path, model, model_index_mapping):
    def add_instance(line, model_index_mapping, session):
        # Check that all foreign keys references exists, otherwise skip the entry
        for attribute, val in model_index_mapping.items():
            if 'foreign_key_to' in val and not val['parse_func'](line[val['index']]) in val['id_list']:
                return

        # Using model_index_mapping create a dict of (attribute, value) pairs, where the attribute is the
        # models attribute and the value is the parsed value from the input file.
        params = {attribute: val['parse_func'](line[val['index']])
                  for attribute, val in model_index_mapping.items() if 'association_to' not in val}
        instance = model(**params)
        session.add(instance)

        # Associations
        for attribute, val in model_index_mapping.items():
            association_to_instances = []
            if 'association_to' in val:
                associations = val['parse_func'](line[val['index']])
                for association in associations:

                    # Create or get association
                    exists = True if association['id'] in ASSOCIATION_CACHE[attribute] else False
                    if not exists:
                        associon_to_instance = val['association_to'](**association)
                        ASSOCIATION_CACHE[attribute][association['id']] = associon_to_instance
                        association_to_instances.append(associon_to_instance)
                    else:
                        association_to_instances.append(ASSOCIATION_CACHE[attribute][association['id']])

                # Add associative links
                val['add_association_func'](instance, association_to_instances)

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
        },
        'genres': {
            'index': 14,
            'parse_func': _parse_json_str,
            'association_to': Genre,
            'add_association_func': _add_genres_to_movie,
        },
        'production_companies': {
            'index': 15,
            'parse_func': _parse_json_str,
            'association_to': ProductionCompany,
            'add_association_func': _add_production_companies_to_movie
        },
        'production_countries': {
            'index': 16,
            'parse_func': _parse_production_countries,
            'association_to': ProductionCountry,
            'add_association_func': _add_production_countries_to_movie
        },
        'spoken_languages': {
            'index': 17,
            'parse_func': _parse_spoken_languages,
            'association_to': SpokenLanguage,
            'add_association_func': _add_spoken_languages_to_movie
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


def _parse_json_str(string):
    string = string.replace("'", '"')
    string = string.replace('\\xa0', ' ')
    return json.loads(string)


def _create_id_from_feature(items, feature_name, feature_id_list):
    for item in items:
        if item[feature_name] not in feature_id_list:
            feature_id_list[item[feature_name]] = len(feature_id_list)
        item['id'] = feature_id_list[item[feature_name]]
    return items


def _parse_production_countries(string):
    countries = _parse_json_str(string)
    return _create_id_from_feature(countries, 'iso_3166_1', COUNTRY_IDS)


def _parse_spoken_languages(string):
    languages = _parse_json_str(string)
    return _create_id_from_feature(languages, 'iso_639_1', SPOKEN_LANGUAGE_IDS)


def _add_genres_to_movie(movie_instance, genre_instances):
    movie_instance.genres.extend(genre_instances)


def _add_production_companies_to_movie(movie_instance, production_company_instances):
    movie_instance.production_companies.extend(production_company_instances)


def _add_production_countries_to_movie(movie_instance, production_country_instances):
    movie_instance.production_countries.extend(production_country_instances)


def _add_spoken_languages_to_movie(movie_instance, spoken_language_instances):
    movie_instance.spoken_languages.extend(spoken_language_instances)
