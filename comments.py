import requests
import json
import os


def _read_from_file(file_name='cache/bot-comments.json'):
  with open(file_name, 'r') as f:
    content = f.read()
    return json.loads(content)


def get_comments(api_result):
  return [ Comment.from_json(c) for c in api_result.get('data').get('children')]


class Comment(object):


  registry = {}
  bot_comments = None

  def __init__(self, confirmed, body, parent, link, id):
    self.confirmed = confirmed
    self.body = body
    self._parent = parent
    self.link = link
    self.id = id 
    Comment.registry[id] = self

  @property
  def parent(self):
    return Comment.registry.get(self._parent)


  @classmethod
  def from_json(classs, from_json):
    data = from_json.get('data')
    confirmed = data.get('body').startswith('Confirmed')
    parent = data.get('parent_id')[3:]
    link =  data.get('link_id')[3:]
    id = data.get('id')
    return Comment(confirmed,data.get('body'),parent,link,id)

  @classmethod
  def from_article_comments_list(classs, comments_list):
    if not isinstance(comments_list, dict):
      return
    top_level_comments = comments_list['data']['children']
    for c in top_level_comments:
      if c['kind'] == 't1':
        Comment.from_json(c) 
        replies = c['data']['replies'] 
        Comment.from_article_comments_list(replies)

  def fetch_article_comments(self):
    file_name = "cache/comments-%s.json" % self.link  

    if os.path.isfile(file_name):
      with open(file_name, 'r') as f:
        text = f.read()
        items = json.loads(text)
        return Comment.from_article_comments_list(items[1])

    url = 'http://www.reddit.com/comments/%s.json' % self.link
    headers = {'User-Agent': 'cmv-delta-bot-analysis-parser'}
    
    print 'getting comments for ' + self.link
    comments = requests.get(url, headers=headers)

    with open(file_name, 'w') as f:
      f.write(comments.text.encode('utf8'))

    return Comment.from_article_comments_list(json.loads(comments.text)[1])

  @classmethod
  def fetch_parent_articles(classs, comments):
    for c in comments:
      c.fetch_article_comments()
  
  @classmethod
  def load_all_comments(classs):
    initial_list = get_comments(_read_from_file())
    Comment.bot_comments = [c for c in initial_list if c.confirmed]
    Comment.fetch_parent_articles(initial_list)

  @classmethod
  def get_delta_recievers(classs):
    for comment in Comment.bot_comments:
      parent = comment.parent        
      if parent and parent.parent:
        yield parent.parent


