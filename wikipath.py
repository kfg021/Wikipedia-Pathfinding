# HOW TO USE:
#   
#   Install dependencies:
#       pip3 install requests
#       pip3 install beautifulsoup4
#
#   To run, use the following terminal command:
#       python3 wikipath.py name_of_start_page name_of_end_page maximum_distance
#
#       maximum_distance represents how many 'layers' to search outward from the
#       starting page.
#
#       For the start and end pages, make sure to only include the portion of
#       the URL that comes after 'https://en.wikipedia.org/wiki/'.
#       
#   Sample use:
#       python3 wikipath.py Terence_Tao Leonhard_Euler 3

from collections import deque
import sys
import urllib

from bs4 import BeautifulSoup
import requests


def format_page(page):
    # Makes it more human-readable, renders unicode characters
    return urllib.parse.unquote(page)

def format_path(path):
    path = list(map(format_page, path))
    return ' --> '.join(path)

def shortest_path(start_page, end_page, max_distance):

    # All relevant Wikipedia pages begin with this
    PREFIX = 'https://en.wikipedia.org/wiki/'

    # Wikipedia uses a namespace system to organize its pages. The only relevant
    # namesapce for the search is the main namespace (no prefix) and the rest
    # can be ignored.
    BAD_NAMESPACES = ['User', 'Wikipedia', 'File', 'MediaWiki', 'Template', 'Help', 'Category', 'Portal', 'Draft', 'TimedText', 'Module']

    # A dictionary that stores the pages seen so far, and how far they are from
    # the original page.
    distance = {start_page: 0}

    # A dictionary that stores which page led to a given page.
    parent = {start_page: None}

    # A queue that holds the webpages yet to be explored.
    queue = deque([start_page])

    while queue and end_page not in parent:
        current_page = queue.popleft()

        # Do not expand pages that are already max_distance away from the
        # starting page.
        if distance[current_page] >= max_distance:
            continue
        
        print('Searching', format_page(current_page))

        # Query the webpage. Check to make sure that the site is valid,
        # because it is possible that the user has entered an invalid link.
        # In addition, Wikipedia pages can sometimes contain broken links.
        webpage = requests.get(PREFIX + current_page)
        if not webpage.ok:
            return None

        # Consider all links in the body of the wepbage.
        soup = BeautifulSoup(webpage.content, 'html.parser')
        body = soup.find('div', id='bodyContent')
        for a in body.find_all('a', href=True):
            next_page = a['href']

            # If a link begins with "/wiki/", then it is an internal link.
            if next_page.startswith('/wiki/'):

                # Since all pages have this prefix, there is no need to store it.
                next_page = next_page[len('/wiki/'):]

                # Make sure that the URL links to the full page, not to a fragment
                next_page, _ = urllib.parse.urldefrag(next_page)
                
                # Make sure the current site is not one of the types to avoid
                if not any({next_page.startswith(pref + ':') or next_page.startswith(pref + '_talk:') for pref in BAD_NAMESPACES}):

                    # If this page has not been seen, set its distance
                    # and parent, and add it to the queue.
                    if next_page not in parent:
                        distance[next_page] = distance[current_page]+1
                        parent[next_page] = current_page
                        queue.append(next_page)

    if end_page not in parent:
        return None
    else:
        # Construct the final path
        current = end_page
        path = []
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
        return path

if __name__ == '__main__':
    # Parse command line arguments and run the program
    args = sys.argv
    if len(args) != 4 or not args[3].isdigit():
       print('Invalid arguments!')
    else:
        start, end, max_dist = args[1], args[2], int(args[3])
        path = shortest_path(start, end, max_dist)

        print()
        if path is None:
            print('No path exists!')
        else:
            print('Path found!')
            print(format_path(path))