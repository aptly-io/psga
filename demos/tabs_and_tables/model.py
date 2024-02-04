# Copyright 2024 Francis Meyvis <psga@mikmak.fun>

"""The data model that uses a REST service to manage its data."""

import PySimpleGUI as sg
from requests import HTTPError, Request, Session

import psga

# pylint: disable=no-member,too-few-public-methods


class _RestRequest:
    def __init__(self, window: sg.Window, key: str, request: Request, cookie: str):
        self._cookie = cookie
        window.perform_long_operation(lambda: self._send_request(request), key)

    def _send_request(self, request: Request):
        session = Session()
        response = session.send(session.prepare_request(request))
        try:
            response.raise_for_status()
        except HTTPError as ex:
            response = ex
        return (response, self._cookie)


class Model:
    """Manages the data from a cloud service through REST calls"""

    def __init__(self, dispatcher: psga.Dispatcher, window: sg.Window):
        self._window: sg.Window = window
        self._url: str = "http://localhost:8000/"

        # PSGA: Model does not inherit PSGA.Dispatcher: therefore it manually register its handlers
        dispatcher.register(self._on_refreshed)
        dispatcher.register(self._on_created)
        dispatcher.register(self._on_deleted)

    def _is_exception(self, response, resource):
        if isinstance(response, Exception):
            self._window.write_event_value(resource, response)
            return True
        return False

    @psga.action()  # PSGA: called by _RestRequest's perform_long_operation key
    def _on_refreshed(self, values):
        response, resource = values[self._on_refreshed.name]

        if not self._is_exception(response, resource):
            self._window.write_event_value(resource, response.json())

    @psga.action()
    def _on_created(self, values):
        response, resource = values[self._on_created.name]
        if not self._is_exception(response, resource):
            self._refresh(resource)

    @psga.action()
    def _on_deleted(self, values):
        response, resource = values[self._on_deleted.name]
        if not self._is_exception(response, resource):
            self._refresh(resource)

    def _refresh(self, resource: str):
        request = Request("GET", self._url + resource)
        _RestRequest(self._window, self._on_refreshed.name, request, resource)

    def read(self, resource: str):
        """Reads a model data"""
        self._refresh(resource)

    def create(self, resource: str, **kwargs):
        """Creates a new model data"""
        request = Request("POST", str(self._url) + resource, json=kwargs)
        _RestRequest(self._window, self._on_created.name, request, resource)

    def delete(self, resource: str, resource_id: int):
        """Removes a model data"""
        request = Request("DELETE", str(self._url) + resource + "/" + resource_id)
        _RestRequest(self._window, self._on_deleted.name, request, resource)
