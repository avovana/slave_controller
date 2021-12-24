# slave_controller
 - Receives data from scanner
 - Display current status
 - Interact with user
 - Communicate with the [ master controller](https://github.com/avovana/master_labeling/blob/master/README.md)
 - Request tasks
 - Send scan file

Apache Thrift 
PyQt for GUI
QtSocket for TCP communucation with master controller
Queue for GUI and TCP client interaction

| Component | Purpose |
| ------ | ------ |
| Apache Thrift | RPC for scanner lib and main programm interaction |
| PyQt | For GUI |
| QtSocket | For TCP communucation with the master controller |
| Queue | For GUI and TCP client interaction |
