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

import requests
import sys

from bs4 import BeautifulSoup
from collections import deque

def shortest_path(start_page, end_page, max_distance):

    # All relevant Wikipedia pages begin with this
    PREFIX = 'https://en.wikipedia.org/wiki/'

    # There a some pages on Wikipedia (Help pages, files, etc.) that are not
    # helpful to us. They simply clog up our search and do not usually have
    # any useful links.
    BAD_LINKS = ['Help:', 'File:']

    # A dictionary that stores the pages we have seen so far, and how far
    # they are from the original page.
    distance = {start_page: 0}

    # A dictionary that stores where we came from to reach a given page.
    parent = {start_page: None}

    # A queue that holds the webpages we have yet to explore.
    queue = deque([start_page])

    while queue and end_page not in parent:
        current_page = queue.popleft()

        # If we are already max_distance away, we would not like to expand
        # this site any further.
        if distance[current_page] >= max_distance:
            continue
        
        print('Searching', current_page)

        # Query the webpage. We check to make sure that the site is valid,
        # because it is possible that the user has entered an invalid link.
        # In addition, Wikipedia pages can sometimes contain broken links.
        webpage = requests.get(PREFIX + current_page)
        if not webpage.ok:
            return None

        # Consider all links in the body of the wepbage. Only hyperlinks that
        # are within <p> tags are considered.
        soup = BeautifulSoup(webpage.content, 'html.parser')
        body = soup.find('div', id='bodyContent')
        for paragraph in body.find_all('p'):
            for a in paragraph.find_all('a', href=True):
                next_page = a['href']

                # If a link begins with '/wiki/', then it is an internal link.
                if next_page.startswith('/wiki/'):

                    # Since all pages have this prefix, we don't need to store it.
                    next_page = next_page[len('/wiki/'):]
                    
                    # Make sure the current site is not one of the types we
                    # would like to avoid
                    if not any([next_page.startswith(link) for link in BAD_LINKS]):

                        # If we have not yet seen this page, set its distance
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
            print(' --> '.join(path))