# import sys
# import _thread

import requests
# import validators
from bs4 import BeautifulSoup
from halo import Halo

# import click
# import pathlib

# @click.command()
# @click.argument('url', default='http://christmas-specials.wikia.com/')
# '''Website URL to scrape'''

# @click.argument('data', type=Click.Path())
# 'Name of destination where scraped files should be stored')

def get_soup(url):
    '''
    Returns a BeautifulSoup version of a web page.
    '''
    response = requests.get(url)
    content = response.text
    return BeautifulSoup(content)

def get_links(table):
    '''
    Retrieves links from an embedded tabular structure.
    '''
    links = set()
    for child in table.children:
        for link in child.find_all('a', href=True):
            links.add(link['href'])

    return links


# @click.argument('url')
def main():
    url = 'http://christmas-specials.wikia.com/'
    #data='xmas'
    # if not validators.url(url):
    #     print('Invalid URL')
    # path = pathlib.Path(data)

    spinner = Halo(text='Fetching article list . . .')
    spinner.start()
    
    soup = get_soup(url + '/wiki/Special:AllPages')

    spinner.succeed(text='Fetching list ===> Done')

    '''Process the articles'''

    articles = set()

    spinner = Halo(text='Processing articles . . .')
    spinner.start()

    table_chunks = soup.find('table', 
        {'class': ['allpageslist', 'mw-allpages-table-chunk']})
    
    chunks = set(get_links(table_chunks))

    chunks_done = 0
    chunks_left = len(chunks)

    spinner.text = f'Processing chunks: {chunks_done}/{chunks_left}'

    '''Process the chunks'''

    while len(chunks) > 0:
        current_link = chunks.pop()

        soup = get_soup(url + current_link)
        current_table = soup.find('table', 
        {'class': ['allpageslist', 'mw-allpages-table-chunk']})

        if 'allpageslist' in current_table.get('class'):
            child_chunks = get_links(current_table)
            chunks = chunks.union(child_chunks)
            chunks_left += len(child_chunks)

        if 'mw-allpages-table-chunk' in current_table.get('class'):
            for child in current_table.children:
                for link in child.find_all('a', href=True):
                    article_link = link['href']
                    article = article_link.split('/')[-1]
                    articles.add(article.replace('_', ' '))
        
        chunks_done += 1
        spinner.text = f'Processing chunks: {chunks_done}/{chunks_left}'

    spinner.succeed(text='Processing chunks ===> Done')

    spinner = Halo(text=f'Printing {len(articles)} articles to {path}')
    spinner.start()

    for article in sorted(articles):
        with open('files' + '.txt', 'w') as outfile:
            outfile.write(article)
            outfile.write('\n')

    spinner.succeed(text=f'Printing {len(articles)} articles. ===> Done')

    if  __name__ == "__main__":
        main()
        print('running')