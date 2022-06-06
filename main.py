import sys
import uvicorn

from pprint import pprint as pp

from config import HOST, PORT
from url_gravy.database import Database
from url_gravy.shortener import Shortener
from url_gravy.webapp import app

def parse_args():
    cmd = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        key, val = arg.split('=')
        kwargs[key.strip('-')] = val
    return cmd, kwargs

if __name__ == '__main__':
    cmd, kwargs = parse_args()
    if cmd == 'setup':
        Database().configure_tables()
        print('Tables configured')
    if cmd == 'serve':
        uvicorn.run(app, host=HOST, port=PORT)
    if cmd == 'shorten':
        url = Shortener().execute(**kwargs)
        print(f'URL successfully shortened to {url}')
    if cmd == 'delete':
        Database().delete_records(**kwargs)
        print('Records deleted')
    if cmd == 'inspect':
        pp(Database().get_records(**kwargs))