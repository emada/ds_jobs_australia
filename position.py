import string

class Position:

  __title__             = None
  __url__               = None
  __date__              = None
  __company__           = None
  __city__              = None
  __state__             = None
  __description__       = None
  __description_words__ = None
  __skills__            = None
  __experience__        = None


  def __init__(self, title, url, date, company, city, state):
    self.__title__   = title
    self.__url__     = url
    self.__date__    = date
    self.__company__ = company
    self.__city__    = city
    self.__state__   = state


  # @staticmethod
  # def get_ngrams(words, n=2):
  #   ngrams = []
  #   for i in range(len(words) - n + 1):
  #     ngrams.append(' '.join(words[i:i+n]))

  #   return ngrams



  def set_description(self, description):
    self.__description__ = description


  def get_description_words(self):
    return self.__description_words__


  def get_description(self):
    return self.__description__


  def get_url(self):
    return self.__url__


  def get_skills(self):
    return self.__get_skills__


  def get_experience(self):
    return self.__get_experience__



