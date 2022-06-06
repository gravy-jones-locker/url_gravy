import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, constr
from typing import Optional

from config import MAX_SUFFIX_LEN, BASE_URL
from .shortener import Shortener, URLNotAvailableError
from .database import Database

logger = logging.getLogger('uvicorn')

app = FastAPI()

class Params(BaseModel):
    target: str
    suffix: Optional[constr(min_length=1, max_length=MAX_SUFFIX_LEN)] = None

@app.post('/shorten_url')
def shorten_url(params: Params) -> dict:
    """
    Route a shortening request to the Shortener class and handle errors.
    :param params: the user-defined shortening parameters.
    :return: a dictionary containing a 'short_url' value.
    """
    logger.info(f'*** Shortening URL with params {params}')

    try:  # Attempt to execute the shortening flow
        url = Shortener().execute(params.target, params.suffix)
        logger.info(f'*** Generated new URL {url}')
        return {"short_url": url}

    except Exception as exc:
        if isinstance(exc, URLNotAvailableError) and params.suffix is not None:
            # True if a user-defined suffix is not available
            logger.error('*** User suffix not available. Returning 400')
            raise HTTPException(
                status_code=400,
                detail='This suffix is not available')

        # Otherwise something unexpected has gone wrong..
        logger.error('*** Shortening failed', exc_info=1)

        raise HTTPException(status_code=500, detail='Shortening failed')

@app.get('/{suffix:path}')
def redirect(suffix: str) -> RedirectResponse:
    """
    Handle a request to a shortened URL by redirecting to its target.
    :param suffix: the value which identifies the URL.
    :return: a RedirectResponse to the target URL.
    """
    logger.info(f'*** Handling short URL at {BASE_URL}/{suffix}')
    try:
        record = Database().get_records(suffix=suffix)[0]
        return RedirectResponse(record["target"], status_code=303)
    except:
        logger.error('*** Redirect failed', exc_info=1)
        raise HTTPException(status_code=500, detail='Redirect failed')