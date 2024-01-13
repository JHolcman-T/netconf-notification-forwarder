# Requirements

- Provide ssh server for clients to connect
- Make it possible to change the server implementation to another protocol if needed
- Provide ssh client in order to subscribe to notifications
- Make it possible to change the client implementation to another protocol if needed
- Support for netconf 1.0 and 1.1
- Support chunking
- Support settings
- Forwarding of notifications on the same stream
- Forwarding of notifications on another stream
- Forwarding of notifications on multiple streams at the same time
- Forwarding of notifications from multiple source streams on one outgoing stream
- Logging of actions (info and debug)
- Runnable as script (not interactive) console application
- Runnable as script (interactive) console application
- Hot reloading of settings (i.e. dynamic adding of routes)
- Leave the possibility to run as visual (native) windows app ui
- Leave the possibility to run as webserver
- Structured logging (json, xml, strings)
- SSH server must support following auth methods: username+password, publickey
- Support plugins, make whole project pluggable


# Architecture
In this section I'll briefly describe the architecture of this project.
## Core
- Base server interface that will be used to implement various server connection protocols (ssh, rest, etc.)
- Base logging interface that will be used to implement loggers
- Built-in router
- Built-in subscription manager for incoming and outgoing (client) notifications
- Built-in RPCs

# Package - requirement mappings
## Core
### Logging
- Logging of actions (info and debug)
- Base logging interface that will be used to implement loggers
### Server
- Base server interface that will be used to implement various server connection protocols (ssh, rest, etc.)
- Provide interface to spawn client (async) tasks that will handle client requests
### Client
- Base client interface that will be used to implement various client connection protocols
### SubscriptionManager
- Built-in subscription manager for incoming and outgoing (client) notifications
### Router
- Forwarding of notifications on the same stream
- Forwarding of notifications on another stream
- Forwarding of notifications on multiple streams at the same time
- Forwarding of notifications from multiple source streams on one outgoing stream
### Netconf
- Support for netconf 1.0 and 1.1
- Support chunking
- Built-in RPCs

### Settings
- Support settings

## Pluggable packages
### Logging
- Structured logging (json, xml, strings)
### ServerProtocols
- Make it possible to change the client implementation to another protocol if needed
#### SSH
- SSH server must support following auth methods: username+password, publickey
