from __future__ import division

# Inspired by: https://jessesw.com/Data-Science-Skills

from scrape_it import *
import os
import seaborn as sns
import matplotlib.pyplot as plt
import pickle


job = 'data-science'
url = 'http://jobs.careerone.com.au/search'

max_num_pages = 30
pages_file = '../data/pages.p'
positions_file = '../data/positions.p'
scraped_data_file = '../data/scraped_data.p'



#################################################
# Fetch all job positions
#################################################

if os.path.exists(pages_file):
  pages = load_pages_from_disk(pages_file)
else:
  pages = fetch_and_save_pages(url, job, pages_file,max_num_pages)

if os.path.exists(positions_file):
  positions = load_positons_from_disk(positions_file)
else:
  positions = fetch_positions(pages)
  positions = fetch_descriptions(positions)
  save_positons(positions, positions_file)




#################################################
# Scrape data from job positions
#################################################

preprocess_job_info(positions)
num_positions = len(positions)
stop_words = set(stopwords.words("english"))
words = preprocess_descriptions(positions, stop_words)
counter_words = Counter(words)
skills_dict, job_titles_dict = get_relevant_dict(words)

skills, job_titles = skills_job_titles_dataframe(skills_dict, job_titles_dict, num_positions)
df = build_dataframe(positions)

scraped_data = [positions, skills, job_titles, df]
pickle.dump(scraped_data, open(scraped_data_file, 'wb'))



#################################################
# How are the jobs distributed per date?
#################################################
plt.close('all')
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

plot_name = '../images/jobs_dist_dates'
dates = [p.get_date() for p in positions]
plt.hist(dates, bins=30)  
plt.savefig(plot_name)



#################################################
# How are these jobs distributed over the states?
#################################################
column_name = 'State'
plot_name = '../images/jobs_by_state'

serie = df.groupby(column_name).size()
serie = serie.sort_values(ascending=False)
serie = serie / float(num_positions) * 100
df_dist = pd.DataFrame({'count' : serie}).reset_index()

plt.close('all')
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

ax = sns.barplot(
  data=df_dist, 
  y=column_name, 
  x='count'
)
ax.set(
  xlabel='Percentage',
  ylabel=column_name
)

ax.get_figure().savefig(plot_name)



#################################################
# How are these jobs distributed over the cities?
#################################################
column_name = 'City'
plot_name = '../images/jobs_by_city'

serie = df.groupby(column_name).size()
serie = serie.sort_values(ascending=False)
serie = serie / float(num_positions) * 100
df_dist = pd.DataFrame({'count' : serie}).reset_index()

plt.close('all')
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

ax = sns.barplot(
  data=df_dist, 
  y=column_name, 
  x='count'
)
ax.set(
  xlabel='Percentage',
  ylabel=column_name
)

ax.get_figure().savefig(plot_name)



#################################################
# What is the distribution of the desired/required skill?
#################################################
plt.close('all')
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

plot_name = '../images/skills_distribution'
ax = sns.barplot(
  data=skills, 
  x='percentage', 
  y='skill'
)
ax.set(
  xlabel='Percentage',
  ylabel='Skill'
)
ax.get_figure().savefig(plot_name)



#################################################
# What are the most common job titles?
#################################################
plt.close('all')
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

plot_name = '../images/jobs_by_title'
jobs = job_titles.posts.groupby(job_titles.job_titles).sum()
plt.axis('equal')
plt.pie(jobs, labels=jobs.index)
plt.savefig(plot_name)



#################################################
# How are these jobs distributed by companies?
#################################################
column_name = 'Company'
plot_name = '../images/jobs_by_company'

serie = df.groupby(column_name).size()
serie = serie.sort_values(ascending=False)
serie = serie / float(num_positions) * 100
df_dist = pd.DataFrame({'count' : serie}).reset_index()

plt.close('all')
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

ax = sns.barplot(
  data=df_dist.head(10), 
  y=column_name, 
  x='count'
)
ax.set(
  xlabel='Percentage',
  ylabel=column_name
)

ax.get_figure().savefig(plot_name)



