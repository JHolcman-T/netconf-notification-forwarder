# from unittest import TestCase

import xml.etree.ElementTree as ET
import re
from netconf_notification_forwarder.subscribtion_manager import SubscriptionManager


# class TestServer(TestCase):
#     pass


def namespace(element):
    m = re.match(r"{.*}", element.tag)
    return m.group(0).removeprefix("{").removesuffix("}") if m else ""


def qtag(element):
    ns = namespace(element)
    return ns, element.tag.removeprefix(f"{{{ns}}}")


def is_subscribtion(data):
    xml = ET.fromstring(data)
    rpc_element = xml
    create_subscription_element = xml.find(".//{urn:ietf:params:xml:ns:netconf:notification:1.0}create-subscription")
    stream_element = xml.find(".//{urn:ietf:params:xml:ns:netconf:notification:1.0}stream")
    if None in (rpc_element, create_subscription_element, stream_element):
        return False
    stream = stream_element.text
    message_id = xml.attrib.get("message-id")
    print(message_id, stream)
    return True


def stream():
    manager = SubscriptionManager()
    manager.register_stream("NETCONF")
    manager.register_stream("NETCONF")
    manager.subscribe("NETCONF", "CLIENT1")
    manager.subscribe("NETCONF", "CLIENT2")
    manager.subscribe("NETCONF", "CLIENT3")
    manager.subscribe("NETCONF", "CLIENT4")
    manager.subscribe("NETCONF", "CLIENT5")
    manager.subscribe("NETCONF", "CLIENT6")
    manager.subscribe("NETCONF", "CLIENT7")
    manager.subscribe("NETCONF", "CLIENT7")
    manager.subscribe("NETCONF2", "CLIENT2")
    manager.unsubscribe("NETCONF", "CLIENT1")
    manager.unregister_stream("NETCONF")
    manager.unregister_stream("NETCONF")


if __name__ == "__main__":
    data = (
        '<?xml version="1.0" encoding="UTF-8"?><nc:rpc xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"'
        ' message-id="urn:uuid:77515b67-ba3a-4957-86ab-8992415226cc"><ns0:create-subscription'
        ' xmlns:ns0="urn:ietf:params:xml:ns:netconf:notification:1.0"><ns0:stream>NETCONF</ns0:stream></ns0:create-subscription></nc:rpc>'
    )
    is_subscribtion(data)
    stream()
