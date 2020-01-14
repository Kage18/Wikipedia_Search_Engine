WRITE_PAGES_TO_FILE = 5000

# LEMMATIZER_OR_STEMMER = 'lemmatization'
LEMMATIZER_OR_STEMMER = 'stemming'

# SCORE_TYPE = "freq_ratio"
# SCORE_TYPE_TYPE = float

SCORE_TYPE = "freq"
SCORE_TYPE_TYPE = int

COMPRESS_INDEX = False

TOP_N_RESULTS = 50

CONSIDER_TOP_N_POSTINGS_OF_EACH_WORD = True
TOP_N_POSTINGS_FOR_EACH_WORD = 200000


FIELD_WEIGHTS = {
    't': 2,
    'b': 1,
    'i': 1,
    'c': 1,
    'e': 1
}
