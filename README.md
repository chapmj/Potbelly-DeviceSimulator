# Potbelly-DeviceSimulator

Potbelly-DeviceSimulator is designed to simulate medical devices.  It can respond appropriately to requests and log data received.

### App-Server
**App-Server.py** is provided as a shim to run the simulated device.  It will open a socket and loop waiting for data to be received.  Optionally, a sample ID number can be provided as an argument to generate Manufacturer record messages.

**Example:**

```python2_dir/python App-Server.py```

```python2_dir/python App-Server.py SID12345678```


### App-Client

**App-client.py** is provided as a test driver.  It represents a server connecting to a medical device.

**Example:**

```python2_dir/python App-Client.py```

### Test

A simple test would be to start up both the client and server and wait for data to be exchanged.  Otherwise it can be connected to an ASTM1394 or LIS2A server.  At this moment, the device will only act as server and accept TCP/IP clients.
