from dataclasses import dataclass
import json
from typing import List


@dataclass
class StreamRoute:
    source: List[str]
    destination: List[str]


@dataclass
class Rule:
    hosts: List[str]
    port: int
    streams: List[StreamRoute]

    def get_streams(self):
        return self.get_source_streams().union(self.get_destination_streams())

    def get_source_streams(self):
        return {source for stream_route in self.streams for source in stream_route.source}

    def get_destination_streams(self):
        return {destination for stream_route in self.streams for destination in stream_route.destination}


@dataclass
class Settings:
    rules: List[Rule]

    def get_streams(self):
        return {stream for rule in self.rules for stream in rule.get_streams()}

    def get_source_streams(self):
        return {stream for rule in self.rules for stream in rule.get_source_streams()}

    def get_destination_streams(self):
        return {stream for rule in self.rules for stream in rule.get_destination_streams()}

    @staticmethod
    def from_file(path: str):
        with open(path, "r") as settings_file:
            settings_json = json.load(settings_file)

        rules = list()
        for rule in settings_json.get("rules", []):
            hosts = rule.get("hosts", None)
            port = rule.get("port", None)
            streams = [
                StreamRoute(
                    source=s.get("source", None),
                    destination=s.get("destination", None),
                )
                for s in rule.get("streams", [])
            ]

            rule_obj = Rule(
                hosts=hosts,
                port=port,
                streams=streams,
            )
            rules.append(rule_obj)
        return Settings(rules=rules)
