from os import environ
from spacy import load
import en_core_web_sm
nlp= en_core_web_sm.load()


AWS_ACCESS_KEY_ID = environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = environ['AWS_SECRET_ACCESS_KEY']

CHANNEL_ACCESS_TOKEN = environ['CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET = environ['CHANNEL_SECRET']
