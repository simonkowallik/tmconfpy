# -*- coding: utf-8 -*-
"""Simple API server for tmconfpy"""

import enum
from typing import Union

from fastapi import Body, FastAPI, UploadFile
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from . import (
    __author__,
    __description__,
    __email__,
    __homepage__,
    __license__,
    __projectname__,
    __version__,
)
from .parser import Parser

EXAMPLE_RESPONSES = {
    "parser": {
        200: {
            "description": "Returns the parsed tmconf as JSON object.",
            "content": {
                "application/json": {
                    "examples": {
                        "object": {
                            "summary": "object response",
                            "value": {
                                "ltm profile imap imap": {"activation-mode": "require"},
                                "ltm profile pop3 pop3": {"activation-mode": "require"},
                            },
                        },
                        "tabular": {
                            "summary": "tabular response",
                            "value": [
                                [
                                    "ltm profile imap",
                                    "imap",
                                    {"activation-mode": "require"},
                                ],
                                [
                                    "ltm profile pop3",
                                    "pop3",
                                    {"activation-mode": "require"},
                                ],
                            ],
                        },
                    }
                },
                "application/x-ndjson": {
                    "examples": {
                        "jsonl": {
                            "summary": "jsonl response",
                            "value": [
                                {
                                    "ltm profile imap imap": {
                                        "activation-mode": "require"
                                    }
                                },
                                {
                                    "ltm profile pop3 pop3": {
                                        "activation-mode": "require"
                                    }
                                },
                            ],
                        },
                    }
                },
            },
        }
    },
    "fileparser": {
        200: {
            "description": "Returns the parsed tmconf for all submitted files as JSON objects in an array.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "filename": "imap.tmconf",
                            "output": {
                                "ltm profile imap imap": {"activation-mode": "require"}
                            },
                        },
                        {
                            "filename": "pop3.tmconf",
                            "output": {
                                "ltm profile pop3 pop3": {"activation-mode": "require"}
                            },
                        },
                    ]
                }
            },
        },
    },
}


app = FastAPI(
    openapi_tags=[
        {
            "name": __projectname__,
            "description": __description__,
        },
    ],
    summary=__description__,
    title=__projectname__,
    version=__version__,
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0",
    },
    contact={"name": __author__, "url": __homepage__},
    docs_url="/",
)


class ParserResponseFormat(str, enum.Enum):
    """Response format of parsed tmconf data."""

    object = "object"
    tabular = "tabular"
    jsonl = "jsonl"


class FileParserResult(BaseModel):
    """Result model for the fileparser endpoint."""

    filename: str
    output: dict


@app.post(
    "/fileparser/",
    tags=[__projectname__],
    response_model=list[FileParserResult],
    responses=EXAMPLE_RESPONSES["fileparser"],
    summary="Parse one or multiple files",
)
async def fileparser(
    filename: list[UploadFile],
):
    """
    Submit one or multiple files in multipart/form-data. Returns a JSON object with results for each file.

    Example usage:

    ```shell
    $ curl -s http://localhost:8000/fileparser/ -F 'filename=@example/imap.tmconf' -F 'filename=@example/pop3.tmconf'
    [
        {"filename":"imap.tmconf","output":{"ltm profile imap imap":{"activation-mode":"require"}}},
        {"filename":"pop3.tmconf","output":{"ltm profile pop3 pop3":{"activation-mode":"require"}}}
    ]
    ```
    """
    results: list = []
    for _file in sorted(
        filename, reverse=False, key=lambda upload_file: upload_file.filename
    ):
        data = await _file.read()
        parsed = Parser(data.decode())
        results.append(FileParserResult(filename=_file.filename, output=parsed.dict))

    return results


@app.post(
    "/parser/",
    tags=[__projectname__],
    responses=EXAMPLE_RESPONSES["parser"],
    response_model=None,
    summary="Parse POST data",
)
async def parser(
    tmconf: str = Body(
        media_type="text/plain",
        examples=[
            "ltm profile imap imap {\n    activation-mode require\n}\nltm profile pop3 pop3 {\n    activation-mode require\n}"
        ],
    ),
    response_format: ParserResponseFormat = ParserResponseFormat.object,
) -> Union[Response, JSONResponse]:
    """
    Accepts a POST request with a tmconf file content as the body. Returns a JSON object with the parsed tmconf.

    Example usage:

    ```shell
    $ curl -s http://localhost:8000/parser/ --data-binary @example/imap.tmconf
    {"ltm profile imap imap":{"activation-mode":"require"}}
    ```
    """
    parsed = Parser(tmconf)
    # tabular
    if response_format == ParserResponseFormat.tabular:
        return JSONResponse(content=parsed.tabular)
    # jsonl - jsonlines
    elif response_format == ParserResponseFormat.jsonl:
        return Response(
            # media_type="application/x-ndjson", # fails rendering in Swagger UI
            # media_type="application/jsonl", # https://github.com/wardi/jsonlines/issues/9
            media_type="text/plain",  # most compatible choice
            content=parsed.jsonl,
        )
    # object
    return JSONResponse(content=parsed.dict)
