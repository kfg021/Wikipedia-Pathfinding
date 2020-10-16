# Wikipedia-Pathfinding

## Download repository:
```
git clone https://github.com/kfg021/Wikipedia-Pathfinding
```

## Install dependencies:
```
pip3 install requests
pip3 install beautifulsoup4
```

## Run:
```
python3 wikipath.py name_of_start_page name_of_end_page maximum_distance
```

For the start and end pages, make sure to only include the portion of
the URL that comes after 'https://en.wikipedia.org/wiki/'.

maximum_distance represents how many 'layers' to search outward from the
starting page.
    
## Sample use:
```
python3 wikipath.py Terence_Tao Leonhard_Euler 3
```