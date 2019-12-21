# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import requests
import json
import string
from collections import namedtuple
# import validators
from bs4 import BeautifulSoup, NavigableString
from halo import Halo


def get_soup(url):
    '''
    Returns a BeautifulSoup version of a web page.
    '''
    response = requests.get(url)
    content = response.text
    return BeautifulSoup(content, features='html.parser')


def get_links(table):
    '''
    Retrieves links from an embedded tabular structure.
    '''
    links = set()
    for child in table.children:
        for link in child.find_all('a', href=True):
            links.add(link['href'])

    return links


# %%
url = 'http://christmas-specials.wikia.com/'

spinner = Halo(text='Fetching article list . . .')
spinner.start()

soup = get_soup(url + '/wiki/Special:AllPages')
spinner.succeed(text='Fetching list ===> Done')

'''Process the articles'''

articles = set()

spinner = Halo(text='Processing articles . . .')
spinner.start()

table_chunks = soup.find('table', {
    'class': ['allpageslist', 'mw-allpages-table-chunk']
    })

chunks = set(get_links(table_chunks))

chunks_done = 0
chunks_left = len(chunks)


# %%
# proof of concept

# article = '/wiki/Mr._Monk_and_the_Man_Who_Shot_Santa_Claus'

def get_article_data(article, url='http://christmas-specials.wikia.com/'):
    Article = namedtuple('Article', 'title contents categories related')
    article_soup = get_soup(url + article)
    article_title = article_soup.find('h1').text
    # article_contents = article_soup.find_all('div', {
    #     'class': ['mw-content-ltr', 'mw-content-text',
    #     'mw-collapsible', 'mw-made-collapsible']})

    related = []
    for tag in soup.select('h2 ~ ul > li'):
        related.append((tag.text, tag.a['href']))

    article_contents = ' '.join([p.text for p in article_soup.find_all('p')])
    article_categories = [li['data-name'] for li in
                          article_soup.find_all('li', {
                            'class': 'category normal', 'data-type': 'normal'
                            })]
    article = Article(
                title=article_title,
                contents=article_contents,
                categories=article_categories,
                related=related
                )
    return article

# %%


spinner.text = f'Processing chunks: {chunks_done}/{chunks_left}'

article_data = []
'''Process the chunks'''
while len(chunks) > 0:
    current_link = chunks.pop()
    soup = get_soup(url + current_link)
    current_table = soup.find('table', {
        'class': ['allpageslist', 'mw-allpages-table-chunk']
        })
    if 'allpageslist' in current_table.get('class'):
        child_chunks = get_links(current_table)
        chunks = chunks.union(child_chunks)
        chunks_left += len(child_chunks)
    if 'mw-allpages-table-chunk' in current_table.get('class'):
        for child in current_table.children:
            if isinstance(child, NavigableString):
                continue
            else:
                for link in child.find_all('a', href=True):
                    article_link = link['href']
                    # article = article_link.split('/')[-1]
                    # articles.add((article, article.replace('_', ' ')))
                    try:
                        data = get_article_data(article_link)
                        article_data.append(data)
                        article_path = "_".join(data.title.split().replace(string.punctuation), "")
                        with open(f'{article_path}.json', 'w') as out:
                            json.dump(data._asdict(), out)

                    except Exception as e:
                        print(e, article_link)

    chunks_done += 1
    spinner.text = f'Processing chunks: {chunks_done}/{chunks_left}'

spinner.succeed(text='Processing chunks ===> Done')


# %%
spinner = Halo(text=f'Printing {len(article_data)} articles')
spinner.start()

with open('articles.json', 'w') as out:
    json.dump([article._asdict() for article in article_data], out)

spinner.succeed(text=f'Printing {len(articles)} articles. ===> Done')

__name__ == "__main__"
