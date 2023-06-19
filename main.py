import sys

from pprint import pprint as pp

from url_gravy import shorten, crud, app


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
        crud.create_redirect_table()
        print('Table configured')
    if cmd == 'serve':
        app.serve()
    if cmd == 'shorten':
        url = shorten.execute(**kwargs)
        print(f'URL successfully shortened to {url}')
    if cmd == 'delete':
        crud.delete_redirects(**kwargs)
        print('Records deleted')
    if cmd == 'inspect':
        pp([x.__dict__ for x in crud.get_redirects(filters=kwargs)])
