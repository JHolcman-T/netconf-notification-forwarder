class Router:
    def __init__(self, route_map: dict):
        self._route_map = route_map

    @property
    def route_map(self):
        return self._route_map

    def get(self, stream: str) -> str or None:
        return self._route_map.get(stream, None)
