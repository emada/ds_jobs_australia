import position as pos
from operator import truediv
from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import pickle
from dateutil.parser import parse
import html2text
from collections import Counter
from nltk.corpus import stopwords
import string
from urlparse import urlparse


def fetch_and_save_pages(url, query, pages_file, max_num_pages):
  pages = list()
  page_number = 1
  print(url)
  while page_number < max_num_pages:
    page_content = requests.get(url, 
          params={'q': query, 
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
      
      title   = title.encode('unicode-escape').lower()
      url     = url.encode('unicode-escape').lower()
      company = company.encode('unicode-escape').lower()
      city    = city.encode('unicode-escape').lower()
      state   = state.encode('unicode-escape').lower()
      
      p = pos.Position(title, url, date, company, city, state)
      positions.append(p)

  return positions


def preprocess_job_info(positions):
  for p in positions:
    city = p.get_city()
    city = city.replace(' cbd', '')
    city = city.replace('north', '')
    city = city.title()
    p.set_city(city)

    state = p.get_state()
    state = state.upper()
    p.set_state(state)


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
  all_words = []
  for idx, p in enumerate(positions):
    if p:
      p.preprocess_description(stopwords)
      words = p.get_description_words()
      if words:
        all_words.extend(words)
      else:
        print idx
    else:
      print idx

  return all_words


def get_relevant_dict(words):
  words_freq = Counter(words)
  job_titles_dict = Counter({
      'Data Scientist' : words_freq['data scientist'],
      'data analytics' : words_freq['data analytics'],
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
      'Hadoop'     : words_freq['hadoop'],
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

  phd_dict = Counter({
      'PhD': words_freq['phd']
  })

  machine_dict = Counter({
      'Machine Learning': words_freq['machine learning']
  })

  skills_dict = prog_lang_dict + analysis_tool_dict + hadoop_dict + database_dict + phd_dict
  
  return skills_dict, job_titles_dict


def skills_job_titles_dataframe(skills_dict, job_titles_dict, num_positions):
  skills = pd.DataFrame(skills_dict.items(), columns=['skill', 'posts'])
  job_titles = pd.DataFrame(job_titles_dict.items(), columns=['job_titles', 'posts'])

  skills['percentage'] = skills.posts / float(num_positions) * 100
  job_titles['percentage'] = job_titles.posts / float(num_positions) * 100

  skills = skills.sort_values('posts', ascending=False)
  job_titles = job_titles.sort_values('posts', ascending=False)

  return skills, job_titles


def build_dataframe(positions):
  columns = ['Data Scientist', 'Data Analyst', 'Big Data', 'R', 'Python', 'Java', 'C++', 'Ruby', 'Perl', 'Matlab', 'JavaScript', 'Scala', 'Excel', 'Tableau', 'D3.js', 'SAS', 'SPSS', 'D3', 'Hadoop', 'MapReduce', 'Spark', 'Pig', 'Hive', 'Shark', 'Oozie', 'ZooKeeper', 'Flume', 'Mahout', 'SQL', 'NoSQL', 'HBase', 'Cassandra', 'MongoDB', 'Machine Learning', 'City', 'State']
  columns_dict = Counter({v: 0 for v in columns})
  data = pd.DataFrame(columns=columns)

  for idx, p in enumerate(positions):
    words = p.get_description_words()
    skills_dic, job_titles_dict = get_relevant_dict(words)
    new_row = columns_dict | skills_dic | job_titles_dict
    city = p.get_city()
    state = p.get_state()
    company = p.get_company()
    new_row = new_row | Counter({'City': city})
    new_row = new_row | Counter({'State': state})
    new_row = new_row | Counter({'Company': company})
    data = data.append(new_row, ignore_index=True)

    for k, v in new_row.items():
      if type(v) != str and v > 1:
        print(idx)

  data = data.fillna(0)

  return data


