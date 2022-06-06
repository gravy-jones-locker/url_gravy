# URL Gravy - URL Shortening Demo

## Setup

Use the `pipenv` package (`pip install pipenv`) to configure the required dependencies as a dedicated virtual environment.

    $ pipenv shell
    (url_gravy) $ pipenv install

URL Gravy requires a connection to a working MySQL database. Database settings are defined by the _DB_SETTINGS_ configuration value. The 'urls' and urls_test' tables can then be created with the `setup` command (see below).

## Configuration

Package-level configuration values are defined in `config.py`.

1. _BASE_URL_ - the value which will prefix all the shortened URLs
2. _HOST_ - the webapp host server ip
3. _PORT_ - the webapp host server port
4. _DB_SETTINGS_ - a dictionary of database/user values
5. _MAX_SUFFIX_LEN_ - defines the length of the database 'suffix' field
6. _AUTO_SUFFIX_LEN_ - defines the length of auto-generated suffixes

## Usage
 
### CLI

URL Gravy has a lightweight command line interface for all major shortening-related operations. The basic syntax is `python main.py cmd --arg_name=value`. Arguments in square brackets ([]) are optional.

    Create the requisite db tables
    (url_gravy) $ python main.py setup

    Do URL Shortening
    (url_gravy) $ python main.py shorten --target=https://google.com [--suffix=google_pls]

    Serve the shortening webapp
    (url_gravy) $ python main.py serve

    Delete records (before the specified data)
    (url_gravy) $ python main.py delete [--before_date=YYYYMMDD]

    Retrieve existing records meeting certain criteria
    (url_gravy) $ python main.py inspect [--suffix=google_pls --target=https://google.com id=1]

### Endpoints

The `serve` command exposes two endpoints: 
1. POST requests to **/shorten_url** execute the shortening process with the usual parameter structure ('target' - required; 'suffix' - optional)
2. GET requests to **/[suffix]** redirect to the configured target URL

## Notes

URL Gravy uses the `short_url` package to auto-generate suffixes where one is not supplied. This package leverages integer values to form deterministic alphanumeric scrambles of a specified length.

By using an auto-incrementing database id field to form these scrambles they are guaranteed to be unique for each corresponding record. Assuming a scramble length of 7 characters and an alphabet of 31 characters (the default) this should provide up to **27,512,614,111** unique URLs.

Where suffixes are supplied they are subject to two checks. First, that they do not fall in the set of possible auto-generated URLs and second that they have not already been supplied by other users.