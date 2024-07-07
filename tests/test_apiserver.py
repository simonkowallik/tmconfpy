# -*- coding: utf-8 -*-
"""Test CLI interface"""

# pylint: disable=line-too-long,missing-function-docstring

import pytest  # pylint: disable=unused-import
from fastapi.testclient import TestClient

from tmconfpy.apiserver import app


def test_fileparser():
    """Test fileparser endpoint"""
    client = TestClient(app)
    response = client.post(
        "/fileparser/",
        files=[
            (
                "filename",
                ("imap.tmconf", open("./example/imap.tmconf", "rb"), "text/plain"),
            ),
            (
                "filename",
                ("pop3.tmconf", open("./example/pop3.tmconf", "rb"), "text/plain"),
            ),
        ],
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "filename": "imap.tmconf",
            "output": {"ltm profile imap imap": {"activation-mode": "require"}},
        },
        {
            "filename": "pop3.tmconf",
            "output": {"ltm profile pop3 pop3": {"activation-mode": "require"}},
        },
    ]


class Test_Parser:
    @staticmethod
    def test_default():
        """Test parser endpoint"""
        client = TestClient(app)
        response = client.post(
            "/parser/",
            content=open("./example/imap.tmconf", "rb").read(),
            headers={"Content-Type": "text/plain"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "ltm profile imap imap": {"activation-mode": "require"}
        }

    @staticmethod
    def test_tabular():
        """Test parser endpoint with tabular response format"""
        client = TestClient(app)
        response = client.post(
            "/parser/",
            content=open("./example/imap.tmconf", "rb").read(),
            headers={"Content-Type": "text/plain"},
            params={"response_format": "tabular"},
        )
        assert response.status_code == 200
        assert response.json() == [
            ["ltm profile imap", "imap", {"activation-mode": "require"}]
        ]

    @staticmethod
    def test_jsonl():
        """Test parser endpoint with jsonl response format"""
        client = TestClient(app)
        response = client.post(
            "/parser/",
            content=open("./example/imap.tmconf", "rb").read(),
            headers={"Content-Type": "text/plain"},
            params={"response_format": "jsonl"},
        )
        assert response.status_code == 200
        assert "text/plain" in response.headers["Content-Type"]
        assert (
            response.text
            == r'{"path": "ltm profile imap", "name": "imap", "object": {"activation-mode": "require"}}'
        )
