import os
from datetime import datetime

import main
import pandas as pd
from ratings.database import engine


class MovieLensDS(object):

    def __init__(self, l_from='pkl', ml_dir_path=main.BASE_DIR + os.sep + 'ml-1m',
                 use_ml_1m=True, pkl_files=('movies.pkl', 'users.pkl', 'ratings.pkl')):
        if l_from == 'db':
            connection = engine.connect()
            self.items = pd.read_sql_table('movies', connection)
            self.items = self.items.rename(columns={'id': 'movie_id'})
            if use_ml_1m:  # Only use items present in both Movie Lens 1M and db
                self.ratings = pd.read_csv(ml_dir_path + os.sep + 'ratings.dat', sep='::', engine='python',
                                           names=['user_id', 'movie_id', 'rating', 'timestamp'])
                self.users = pd.read_csv(ml_dir_path + os.sep + 'users.dat', sep='::', engine='python',
                                         names=['user_id', 'gender', 'age', 'occupation', 'zip_code'])
                self.movies_ml = pd.read_csv(ml_dir_path + os.sep + 'movies.dat', sep='::', engine='python',
                                             names=['movie_id', 'title', 'genre'], usecols=['movie_id'])
                self.items = self.movies_ml.merge(self.items, how='inner', on='movie_id')
            else:
                self.ratings = pd.read_sql_table('ratings', connection)
                self.users = pd.DataFrame(self.ratings.user_id.unique(), columns=['user_id'])

        elif l_from == 'pkl':
            self.items = pd.read_pickle(pkl_files[0])
            self.users = pd.read_pickle(pkl_files[1])
            self.ratings = pd.read_pickle(pkl_files[2])
        self.use_ml_1m = use_ml_1m

    def extend_item_attributes(self):
        def table_and_relation_to_dfs(table_name, assoc_table_name, id_col):
            """Load database table and it's associated relation with items

            Parameters:
                table_name (str): Table name in database
                assoc_table_name (str): Name of association table in database
                id_col (str): Column name of foreign key from the association table to the other table

            Returns:
                pd.Dataframe, pd.Dataframe: table, association table"""
            table = pd.read_sql_table(table_name, connection)
            table = table.rename(columns={'id': 'id_col'})
            item_relations_table = pd.read_sql_table(assoc_table_name, connection)
            if self.use_ml_1m:
                item_relations_table = item_relations_table.loc[
                    item_relations_table.movie_id.isin(self.items.movie_id)]
                table = table.loc[table.id_col.isin(item_relations_table[id_col])]
            return table, item_relations_table

        def extend_with_attribute_relation(attribute, relation, rel_id_name, rel_cols_names):
            """Add a new column of boolean values, where true means the item has a relation to the attribute

            Parameters:
                attribute (pd.Dataframe): A dataframe containing the attribute.
                relation (pd.Dataframe): The association table.
                rel_id_name (str): The column name of the foreign key column in the association table to the items.
                rel_cols_names (str or list(int)): The values of the attribute to form the new column in self.items"""
            item_ids = relation[getattr(relation, rel_id_name) == attribute.id_col]['movie_id'].to_numpy()
            if isinstance(rel_cols_names, str):
                rel_cols_names = [rel_cols_names]
            if item_ids.size != 0:
                self.items[
                    '_'.join([str(attribute[name]) for name in rel_cols_names])
                ] = self.items['movie_id'].isin(item_ids)

        connection = engine.connect()

        # Extend with genres
        timer = datetime.now()
        genres, movie_genres = table_and_relation_to_dfs('genres', 'movie_has_genre', 'genre_id')
        genres.apply(lambda x: extend_with_attribute_relation(x, movie_genres, 'genre_id', 'name'), axis=1)
        print(f'genres done. Took {datetime.now() - timer}')

        # Extend with production_companies
        timer = datetime.now()
        production_companies, movie_production_companies = table_and_relation_to_dfs(
            'production_companies', 'movie_has_production_company', 'production_company_id')
        production_companies.apply(
            lambda x:
            extend_with_attribute_relation(x, movie_production_companies, 'production_company_id', 'name'), axis=1)
        print(f'production_companies done. Took {datetime.now() - timer}')

        # Extend with production_countries
        timer = datetime.now()
        countries, movie_countries = table_and_relation_to_dfs(
            'production_countries', 'movie_has_production_country', 'production_country_id')
        countries.apply(
            lambda x:
            extend_with_attribute_relation(x, movie_countries, 'production_country_id', 'iso_3166_1'), axis=1)
        print(f'production_countries done. Took {datetime.now() - timer}')

        # Extend with spoken_language
        timer = datetime.now()
        languages, movie_languages = table_and_relation_to_dfs(
            'spoken_languages', 'movie_has_spoken_language', 'spoken_language_id')
        languages.apply(
            lambda x: extend_with_attribute_relation(x, movie_languages, 'spoken_language_id', 'iso_639_1'), axis=1)
        print(f'production_countries done. Took {datetime.now() - timer}')

        # Extend with actors
        timer = datetime.now()
        actors, movie_actors = table_and_relation_to_dfs('actors', 'movie_has_actor', 'actor_id')
        actors.apply(lambda x: extend_with_attribute_relation(x, movie_actors, 'actor_id', ['name', 'id_col']), axis=1)
        print(f'actors done. Took {datetime.now() - timer}')

        # Extend with crew
        timer = datetime.now()
        crew_members, movie_crew = table_and_relation_to_dfs('crew_members', 'movie_has_crew_member', 'crew_member_id')
        crew_members.apply(
            lambda x: extend_with_attribute_relation(x, movie_crew, 'crew_member_id', ['job', 'name']), axis=1)
        print(f'crew done. Took {datetime.now() - timer}')

    def to_pkl(self, items_path='movies.pkl', users_path='users.pkl', ratings_path='ratings.pkl'):
        self.items.to_pickle(items_path)
        self.users.to_pickle(users_path)
        self.ratings.to_pickle(ratings_path)
