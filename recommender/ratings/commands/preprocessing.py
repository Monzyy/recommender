import pandas as pd


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
                     'poster_path', 'release_date', 'revenue', 'runtime', 'status', 'tagline', 'video', 'genres',
                     'production_companies', 'production_countries', 'spoken_languages']]

    movies['production_companies'] = movies['production_companies'].apply(lambda x: _parse_json_str(x))

    # merge links and movies
    joined = links.merge(movies, left_on='tmdbId', right_on='id', how='left').drop(['tmdbId', 'id'], axis=1)

    # rename columns
    joined.columns = ['id', 'title', 'summary', 'budget', 'adult', 'original_language', 'original_title',
                      'poster_path', 'release_date', 'revenue', 'runtime', 'status', 'tagline', 'video', 'genres',
                      'production_companies', 'production_countries', 'spoken_languages']

    # set budget to int
    joined.budget = joined.budget.fillna(0).astype(int)

    # remove duplicates
    joined = joined.dropna()
    joined = joined.drop_duplicates('id')

    # write back to disk
    joined.to_csv(movie_out_path, index=False)


def _parse_json_str(string):
    def handle_quotes(string, quote_type):
        dd_quote_index = string.find(quote_type)
        other_dd_quote_index = string.find(quote_type, dd_quote_index + len(quote_type))
        if dd_quote_index != -1 and other_dd_quote_index != -1:
            other_dd_quote_index = string.find(quote_type, dd_quote_index + len(quote_type))
            first_part = string[:dd_quote_index]
            mid_part = string[dd_quote_index + 1: other_dd_quote_index]
            rest = string[other_dd_quote_index + 1:]
            if '\'' in mid_part:
                handled_part = first_part + '\'' + mid_part.replace('\'', '') + '\''
            else:
                handled_part = first_part + mid_part
            return handled_part + handle_quotes(rest, quote_type)
        else:
            return string

    # Handle strings that contain single quotes and double quotes
    string = handle_quotes(string, quote_type='"')
    string = string.replace('"', '')
    return string
