import argparse
import os

import config

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)


def load_dataset(args):
    # Import after the configurations are set.
    from ratings.database import init_db
    from ratings.commands.load_movies_dataset import load_movies, load_ratings
    from ratings.commands.preprocessing import preprocess_movies

    # Ask for confirmation
    answer = input('Loading the dataset will clear the current database.\nDo you want to continue? [y/N]')
    if answer.lower() != 'y':
        print('Abort.')
        return

    dir = args.dir if args.dir else BASE_DIR + '/the-movies-dataset'
    init_db()

    cleaned_movies_path = dir + '/cleaned_movies_metadata.csv'
    preprocess_movies(dir + '/movies_metadata.csv', cleaned_movies_path, dir + '/links.csv', dir + '/credits.csv')

    load_movies(cleaned_movies_path)

    # Load ratings
    if args.small_dataset:
        load_ratings(dir + '/ratings_small.csv')
    else:
        load_ratings(dir + '/ratings.csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Parser arguments
    parser.add_argument('--config', default='LOCAL',
                        help='Configurations to use.')
    subparsers = parser.add_subparsers(help='Sub-command help')

    # Load dataset parser
    load_ds_parser = subparsers.add_parser('load_dataset', help='Load dataset into database.')
    load_ds_parser.add_argument('--dir', nargs='?',
                                help='Directory where the dataset is located.')
    load_ds_parser.add_argument('--small_dataset', action='store_true',
                                help='Load the small dataset. Use this when debugging.')
    load_ds_parser.set_defaults(func=load_dataset)

    # Parse args and load configs
    args = parser.parse_args()
    config.set_settings(args.config)

    # Call selected function with arguments
    # https://docs.python.org/3.7/library/argparse.html#argparse.ArgumentParser.add_subparsers
    args.func(args)
