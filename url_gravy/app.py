import os
import uvicorn
import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, constr
from typing import Optional

from url_gravy import crud
from url_gravy.shorten import execute, URLNotAvailableError


logger = logging.getLogger('uvicorn')

app = FastAPI()

class Params(BaseModel):
    target: str
    suffix: Optional[
        constr(  # Do validation on user suffix choices
            min_length=1,
            max_length=int(os.environ["MAX_SUFFIX_LEN"]),
    )] = None

@app.post('/shorten_url')
def shorten_url(params: Params) -> dict:
    """
    Route a shortening request to the Shortener class and handle errors.
    :param params: the user-defined shortening parameters.
    :return: a dictionary containing a 'short_url' value.
    """
    try:  # Attempt to execute the shortening flow
        return {"short_url": execute(params.target, params.suffix)}
    except URLNotAvailableError:
        if params.suffix is not None:
            # True if a user-defined suffix is not available
            raise HTTPException(400, detail='This suffix is not available')
    except:  # True if something unexpected went wrong
        logger.error('Shortening failed', exc_info=True)
        raise HTTPException(500, detail='Shortening failed')

@app.get('/{suffix:path}')
def redirect(suffix: str) -> RedirectResponse:
    """
    Handle a request to a shortened URL by redirecting to its target.
    :param suffix: the value which identifies the URL.
    :return: a RedirectResponse to the target URL.
    """
    try:
        url = crud.get_redirect_url(suffix)
        if url is None:
            raise HTTPException(404, 'Path not found')
        return RedirectResponse(url, 303)
    except:  # True if something unexpected went wrong
        logger.error('Redirect failed', exc_info=True)
        raise HTTPException(status_code=500, detail='Redirect failed')

def serve() -> None:
    uvicorn.run(app, host=os.environ["APP_HOST"], port=int(os.environ["APP_PORT"]))
