from os import environ
import sputnik
import spacy.about

package = sputnik.install('spacy', spacy.about.__version__, spacy.about.__default_model__)


AWS_ACCESS_KEY_ID = environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = environ['AWS_SECRET_ACCESS_KEY']

CHANNEL_ACCESS_TOKEN = environ['CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET = environ['CHANNEL_SECRET']
