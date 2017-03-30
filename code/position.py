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


  def preprocess_description(self, stop_words):
    self.__description_words__ = []
    if self.__description__:
      text = self.__description__.strip().lower()
      text = text.encode('unicode-escape')
      text = text.translate(None, string.punctuation)

      words = text.split(' ')
      if words:
        words = [w for w in words if not w in stop_words]

        # ngrams = get_ngrams(words)
        n = 2
        ngrams = []
        for i in range(len(words) - n + 1):
          ngrams.append(' '.join(words[i:i+n]))
        
        ngrams = [w if w != 'data science' else 'data scientist' for w in ngrams]
        ngrams = [w if w != 'data analyst' else 'data analytics' for w in ngrams]
        ngrams = [w if w != 'data analysis' else 'data analytics' for w in ngrams]
        # text.replace('data science',  'data scientist')
        # text.replace('data analyst',  'data analytics')
        # text.replace('data analysis', 'data analytics')

        ngrams = list(set(ngrams))
        words  = list(set(words))

        # Counter({'data science': 86, 'Data Scientist': 48, 'data analytics': 37, 'data analysis': 26, 'Data Analyst': 4})
        
        self.__description_words__.extend(ngrams)
        self.__description_words__.extend(words)


  def set_description(self, description):
    self.__description__ = description


  def get_description_words(self):
    return self.__description_words__


  def get_description(self):
    return self.__description__


  def get_url(self):
    return self.__url__


  def get_skills(self):
    return self.__skills__


  def get_experience(self):
    return self.__experience__


  def get_city(self):
    return self.__city__


  def set_city(self, city):
    self.__city__ = city


  def get_state(self):
    return self.__state__

  
  def set_state(self, state):
    self.__state__ = state


  def get_date(self):
    return self.__date__


  def get_company(self):
    return self.__company__



