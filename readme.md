# URL Gravy - URL Shortening Demo

## Setup

Use the `pipenv` package (`pip install pipenv`) to configure the required dependencies as a dedicated virtual environment.

    $ pipenv shell
    (url_gravy) $ pipenv install

`.env_example` should be renamed to `.env` and appropriate values set before use.

URL Gravy connects to an sqlite db file. This can be configured using the `setup` command (see below).

## Configuration

Package-level configuration values are defined in `.env`.

2. **APP_HOST** - the webapp host server ip
3. **APP_PORT** - the webapp host server port
4. **DB_HOST** - the sqlite database host value (e.g. `sqlite:///./database.db`)
5. **MAX_SUFFIX_LEN** - defines the length of the database 'suffix' field
6. **AUTO_SUFFIX_LEN** - defines the length of auto-generated suffixes

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
    (url_gravy) $ python main.py delete [--before_date=YYYY-MM-DD]

    Retrieve existing records meeting certain criteria
    (url_gravy) $ python main.py inspect [--suffix=google_pls --target=https://google.com --id=1]

### Endpoints

The `serve` command exposes two endpoints: 
1. POST requests to **/shorten_url** execute the shortening process. The payload must contain a 'target' value and an optional 'suffix' value. A 'short_url' value is contained in the response json object.

2. GET requests to **/[suffix]** redirect to the configured target URL

## Notes

URL Gravy uses the `short_url` package to auto-generate suffixes where one is not supplied. This package uses integer values to form deterministic alphanumeric scrambles of a specified length.

By using an auto-incrementing database id field these scrambles are guaranteed to be unique for each corresponding record. Assuming a scramble length of 7 characters and an alphabet of 31 characters (the default) this should provide up to **27,512,614,111** unique URLs.

Where suffixes are supplied they are subject to two checks. First, that they do not fall in the set of possible auto-generated URLs and second that they have not already been supplied by other users.
