# slave_controller
 - Receives data from the Zebra scanner
 - Display current status
 - Interact with user
 - Communicate with the [ master controller](https://github.com/avovana/master_labeling/blob/master/README.md)
 - Request tasks
 - Send scan file

| Component | Purpose |
| ------ | ------ |
| Zebra devtool | Library for receiving scans |
| Apache Thrift | RPC for scanner lib and main programm interaction |
| PyQt | For GUI |
| QtSocket | For TCP communucation with the master controller |
| Queue | For GUI and TCP client interaction |
