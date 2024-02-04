# Copyright 2024 Francis Meyvis <psga@mikmak.fun>

"""
A built-in mock REST server in a background thread

It serves on localhost:8000 for the paths "/demo/trails" and "/demo/cities"
"""

# pylint: disable=missing-function-docstring

import contextlib
import threading
import time
from http import HTTPStatus
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class Server(uvicorn.Server):
    """Run uvicorn inside a thread"""

    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()

    @staticmethod
    def make_server() -> "Server":
        return Server(uvicorn.Config("rest:app", log_level="warning"))


class Place(BaseModel):
    """Model for a trail of city"""

    id: int
    name: str
    description: str
    location: str


TRAILS: Dict[int, Place] = {
    place["id"]: Place.model_validate(place)
    for place in [
        {
            "id": 1,
            "name": "Ninglinspo",
            "description": "Along the only Belgian mountain river Ninglinspo",
            "location": "Aywaille",
        },
        {
            "id": 2,
            "name": "Le Hérou",
            "description": "A unique rock wall in a Meander of the Ourthe river",
            "location": "Ollomont",
        },
        {
            "id": 3,
            "name": "Mullerthal Place",
            "description": "Nicknamed 'Little Switzerland' due to its craggy terrain,\nthick forests, caves and myriad small streams",
            "location": " Canton of Echternach",
        },
        {
            "id": 4,
            "name": "Pink granite Coast",
            "description": "Coastal Place with unusual pink sand and rock formations",
            "location": "Ploumanac'h",
        },
    ]
}


CITIES: Dict[int, Place] = {
    place["id"]: Place.model_validate(place)
    for place in [
        {
            "id": 1,
            "name": "Dinan",
            "description": "A medieval walled Breton town",
            "location": "Dinan",
        },
        {
            "id": 2,
            "name": "Bruges",
            "description": "A Flemish medieval historic town",
            "location": "Bruges",
        },
        {
            "id": 3,
            "name": "Ubud",
            "description": "Bustling Indonesian town in Bali Island",
            "location": "Bali",
        },
    ]
}


async def _check_exists(resource: Dict[int, Place], id_: int):
    if id_ not in resource:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Not found ({id_})")


async def _get(resource: Dict[int, Place]) -> List[Place]:
    return resource.values()


async def _post(resource: Dict[int, Place], body: Place) -> Place:
    if body.id in resource:
        raise HTTPException(HTTPStatus.BAD_REQUEST, f"Exist already ({body.id})")
    resource[body.id] = body
    return body


async def _read(resource: Dict[int, Place], id_: int) -> Place:
    _check_exists(resource, id_)
    return resource[id_]


async def _update(resource: Dict[int, Place], id_: int, body: Place) -> Place:
    _check_exists(resource, id_)
    if id_ != body.id:
        raise HTTPException(HTTPStatus.BAD_REQUEST, f"Id's mismatch ({id_} != {body.id})")
    resource[id_] = body
    return body


async def _delete(resource: Dict[int, Place], id_: int) -> Place:
    _check_exists(resource, id_)
    result = resource[id_]
    del resource[id_]
    return result


# REST server

app = FastAPI()


@app.get("/demo/trails", tags=["trails"])
async def list_trails() -> List[Place]:
    return await _get(TRAILS)


@app.post("/demo/trails", tags=["trails"])
async def create_trail(body: Place) -> Place:
    return await _post(TRAILS, body)


@app.get("/demo/trails/{id_}", tags=["trails"])
async def read_trail(id_: int) -> Place:
    return await _read(TRAILS, id_)


@app.put("/demo/trails/{id_}", tags=["trails"])
async def update_trail(id_: int, body: Place) -> Place:
    return await _update(TRAILS, id_, body)


@app.delete("/demo/trails/{id_}", tags=["trails"])
async def delete_trail(id_: int) -> Place:
    return await _delete(TRAILS, id_)


@app.get("/demo/cities", tags=["cities"])
async def list_cites() -> List[Place]:
    return await _get(CITIES)


@app.post("/demo/cities", tags=["cities"])
async def create_city(body: Place) -> Place:
    return await _post(CITIES, body)


@app.get("/demo/cities/{id_}", tags=["cities"])
async def read_city(id_: int) -> Place:
    return await _read(CITIES, id_)


@app.put("/demo/cities/{id_}", tags=["cities"])
async def update_city(id_: int, body: Place) -> Place:
    return await _update(CITIES, id_, body)


@app.delete("/demo/cities/{id_}", tags=["cities"])
async def delete_city(id_: int) -> Place:
    return await _delete(CITIES, id_)
