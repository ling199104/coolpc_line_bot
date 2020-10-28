from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot import ChatBot
from models.parser import CoolPcCrawler
import re

first_soup = CoolPcCrawler.get_response()
cool_pc_data = CoolPcCrawler.get_data(first_soup)

chat_bot = ChatBot('Cool_PC_Raw')

trainer_corpus = ChatterBotCorpusTrainer(chat_bot)
trainer_corpus.train(
    "chatterbot.corpus.english",
    "chatterbot.corpus.traditionalchinese",
    # "chatterbot.corpus.japanese"
)

# train with chinese character and first 10 word
# trainer_list = ListTrainer(chat_bot)
# for cool_pc_dataset in cool_pc_data:
#     for item in cool_pc_dataset[-1]:
#         # mix_words = ' '.join(re.findall(re.compile(u"[\u4e00-\u9fa5a-zA-Z0-9]+"), item))
#         # trainer_list.train([mix_words, item])
#         # trainer_list.train([item[0:15], item])
#         # trainer_list.train([item, item])
#         chinese_words = ' '.join(re.findall(re.compile(u"[\u4e00-\u9fa5]+"), item))
#         trainer_list.train([chinese_words, item])
#         english_words = ' '.join(re.findall(re.compile(u"[a-zA-Z0-9]+"), item))
#         trainer_list.train([english_words, item])
