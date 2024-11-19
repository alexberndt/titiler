"""Test TiTiler render extension."""

import os

from fastapi import FastAPI
from rio_tiler.io import STACReader
from starlette.testclient import TestClient

from titiler.core.factory import TilerFactory
from titiler.extensions import renderExtension

stac_item = os.path.join(os.path.dirname(__file__), "fixtures", "item.json")


def test_renderExtension():
    """Test renderExtension class."""
    tiler = TilerFactory()
    tiler_plus_render = TilerFactory(reader=STACReader, extensions=[renderExtension()])
    # Check that we added one route (/renders)
    assert len(tiler_plus_render.router.routes) == len(tiler.router.routes) + 1

    app = FastAPI()
    app.include_router(tiler_plus_render.router)
    with TestClient(app) as client:
        response = client.get("/renders", params={"url": stac_item})
        assert response.status_code == 200
