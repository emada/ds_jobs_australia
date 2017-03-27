# Inspired by: https://jessesw.com/Data-Science-Skills/


from __future__ import division
from operator import truediv
from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import pickle
import os
from dateutil.parser import parse
import html2text
from collections import Counter
from nltk.corpus import stopwords
import string
from urlparse import urlparse
import seaborn as sns
# import nltk
# nltk.download('stopwords')


os.chdir('/Users/ema/datascience/General Assembly (Sydney, 2017)/side_project/data_science_jobs_australia')
import position as pos
# from position import *


job = 'data-science'
url = 'http://jobs.careerone.com.au/search'
pages_file = '/Users/ema/datascience/General Assembly (Sydney, 2017)/side_project/data_science_jobs_australia/pages.p'
positions_file = '/Users/ema/datascience/General Assembly (Sydney, 2017)/side_project/data_science_jobs_australia/positions.p'

MAX_NUM_PAGES = 30



def fetch_and_save_pages(url, pages_file):
  pages = list()
  page_number = 1
  print(url)
  while page_number < MAX_NUM_PAGES:
    page_content = requests.get(url, 
          params={'q': 'data-science', 
                  'page': page_number, 
                  'sort': 'dt.rv.di'})
    status_code = page_content.status_code

    if status_code != 200:
      break

    pages.append(page_content)
    print('{}: {}\n{}'.format(page_number, page_content, page_content.url))
    
    page_number = page_number + 1

  if pages:
    pickle.dump(pages, open(pages_file, 'wb'))

  return pages


def load_pages_from_disk(pages_file):
  return pickle.load(open(pages_file, 'rb'))


def fetch_positions(pages):
  positions = list()
  for p in pages:

    soup = BeautifulSoup(p.text, 'html.parser')
    title_div     = soup.select('div.js_result_container div.jobTitle')
    date_div      = soup.select('div.js_result_container div.postedDate')
    location_div  = soup.select('div.js_result_container div.location')
    company_div   = soup.select('div.js_result_container div.company')

    for t, d, l, c in zip(title_div, date_div, location_div, company_div):
      title   = t.find('span').text if t.find('span') else ''
      url     = t.find('a').get('href') if t.find('a') else ''
      date    = parse(d.find('time')['datetime']) if d.find('time')['datetime'] else ''
      city    = l.find('meta', {'itemprop': 'addressLocality'})
      city    = city['content'] if city else ''
      state   = l.find('meta', {'itemprop': 'addressRegion'})
      state   = state['content'] if state else ''
      company = c.find('a')['title'] if c.find('a') else ''
      p = pos.Position(title, url, date, company, city, state)
      positions.append(p)

  return positions


def fetch_descriptions(positions):
  counter = 0

  for p in positions:

    if counter % 10 == 0:
      print('counter: {}/{}'.format(counter, len(positions)))

    url = p.get_url()
    url_domain = urlparse(url).netloc
    page_content = requests.get(url)
    soup = BeautifulSoup(page_content.text, 'html.parser')

    if url_domain == 'job-openings.monster.com':
      div = {'class': 'jobview-section'}
    elif url_domain == 'jobview.careerone.com.au':
      div = {'id': 'lux-job-input-description'}
    else:
      div = {}
      print('Don\'t know how to parse the hmtl job page')

    description = soup.find('div', div)

    if description:
      description = description.text
      p.set_description(description)
      # print(description[:60])
    else:
      print('{}:'.format(counter))
      print(url)

    counter = counter + 1

  return positions


def save_positons(positions, positions_file):
  pickle.dump(positions, open(positions_file, 'wb'))


def load_positons_from_disk(positions_file):
  return pickle.load(open(positions_file, 'rb'))


def preprocess_descriptions(positions, stopwords):
  res = []
  for idx, p in enumerate(positions):
    if p:
      words = p.preprocess_description(stopwords)
      if words:
        res.extend(words)
      else:
        print idx
    else:
      print idx

  return res


def preprocess_descriptions(positions, stop_words):
  description_words = []
  for p in positions:
    description = p.get_description()
    if description:
      text = description.strip().lower()
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
        ngrams = list(set(ngrams))
        words  = list(set(words))
        description_words.extend(ngrams)
        description_words.extend(words)

  return description_words


# def ngram_descriptions(positions, n):
#   ngrams = []
#   for p in positions:
#     words = p.get_description_words()
#     for i in range(len(words) - n + 1):
#       ngrams.append(' '.join(words[i:i+n]))

#   return ngrams


def get_relevant_desc(words_freq):
  job_title_dict = Counter({
      'Data Scientist'   : words_freq['data scientist'] + words_freq['data science'],
      'Data Analyst' : words_freq['data analyst'] + words_freq['data analysis'] + words_freq['data analytics'],
      'Big Data'       : words_freq['big data'],
  })

  prog_lang_dict = Counter({
      'R'          : words_freq['r'],
      'Python'     : words_freq['python'],
      'Java'       : words_freq['java'],
      'C++'        : words_freq['c++'],
      'Ruby'       : words_freq['ruby'],
      'Perl'       : words_freq['perl'],
      'Matlab'     : words_freq['matlab'],
      'JavaScript' : words_freq['javascript'],
      'Scala'      : words_freq['scala']
  })
                        
  analysis_tool_dict = Counter({
      'Excel'      : words_freq['excel'],
      'Tableau'    : words_freq['tableau'],
      'D3.js'      : words_freq['d3.js'],
      'SAS'        : words_freq['sas'],
      'SPSS'       : words_freq['spss'],
      'D3'         : words_freq['d3']
  })  

  hadoop_dict = Counter({
      'Hadoop'     : words_freq['hadoop_dict'],
      'MapReduce'  : words_freq['mapreduce'],
      'Spark'      : words_freq['spark'],
      'Pig'        : words_freq['pig'],
      'Hive'       : words_freq['hive'],
      'Shark'      : words_freq['shark'],
      'Oozie'      : words_freq['oozie'],
      'ZooKeeper'  : words_freq['zookeeper'],
      'Flume'      : words_freq['flume'],
      'Mahout'     : words_freq['mahout']
  })

  database_dict = Counter({
      'SQL'        : words_freq['sql'],
      'NoSQL'      : words_freq['nosql'],
      'HBase'      : words_freq['hbase'],
      'Cassandra'  : words_freq['cassandra'],
      'MongoDB'    : words_freq['mongodb']
  })

  # machine_dict = Counter({
  #     'Recommendation Engine' : words_freq['recommendation engine'] + words_freq['recommendation system'] + words_freq['recommender engine'] + words_freq['recommender system'],
  # })
  # print(machine_dict)

  skills_data = prog_lang_dict + analysis_tool_dict + hadoop_dict + database_dict
  
  # skills_data = {}
  # skills_data['job_title_dict'] = job_title_dict
  # skills_data['prog_lang_dict'] = prog_lang_dict
  # skills_data['analysis_tool_dict'] = analysis_tool_dict
  # skills_data['hadoop_dict'] = hadoop_dict
  # skills_data['database_dict'] = database_dict
  
  skills = pd.DataFrame(skills_data.items(), columns = ['skill', 'posts'])
  
  job_titles = pd.DataFrame(job_title_dict.items(), columns = ['job_titles', 'posts'])

  return skills, job_titles



# pages = fetch_and_save_pages(url, pages_file)
# pages = load_pages_from_disk(pages_file)
# positions = fetch_positions(pages)
# positions = fetch_descriptions(positions)
# save_positons(positions, positions_file)
positions = load_positons_from_disk(positions_file)
stop_words = set(stopwords.words("english"))
words = preprocess_descriptions(positions, stop_words)
words_freq = Counter(words)
skills, job_titles = get_relevant_desc(words_freq)
number_positions = len(positions)
skills['percentage'] = skills.posts / float(number_positions) * 100
job_titles['percentage'] = job_titles.posts / float(number_positions) * 100
skills = skills.sort_values('posts', ascending=False)
job_titles = job_titles.sort_values('posts', ascending=False)

print(skills)
print(job_titles)

sns.barplot(data=skills, x='percentage', y='skill')
sns.plt.show()

sns.barplot(data=job_titles, x='percentage', y='job_title')
sns.plt.show()




