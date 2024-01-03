from dataclasses import dataclass
from typing import Union, List
from . import get_logger


class Router:
    def __init__(self):
        self._route_map_table = dict()
        self._hosts_map = dict()
        self.log = get_logger("router")

    @dataclass
    class _TableEntry:
        key: str
        route_map: dict

    @property
    def route_map_table(self):
        return self._route_map_table

    def _get_table_entry_by_route_map(self, route_map: dict) -> Union[_TableEntry, None]:
        existing_map = list(filter(lambda item: item[1] == route_map, self._route_map_table.items()))
        # check for duplicate route_maps
        assert 0 <= len(existing_map) <= 1
        return self._TableEntry(*existing_map[0]) if existing_map else None

    def add_route_map_table_entry(self, source_addresses: List[str], source_port: int, route_map: dict) -> int:
        table_entry = self._get_table_entry_by_route_map(route_map)

        if table_entry:
            # get existing key
            key = table_entry.key
        else:
            # generate new key
            key = len(self._route_map_table.keys()) + 1
            # create new entry in route_map
            self._route_map_table[key] = route_map

        # add host -> key mapping
        for source_address in source_addresses:
            self._hosts_map[(source_address, source_port)] = key

        return key

    def get_destinations(self, source_address: str, source_port: int, stream: str) -> str or None:
        key = self._hosts_map.get((source_address, source_port), None)
        route_map = self._route_map_table.get(key, dict())
        return route_map.get(stream, None)
