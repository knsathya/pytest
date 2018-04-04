# pytest
Python based test scripts

This test framework is mainly used for performing coordinated testing in host:remote architeure. In host:remote test model, we have might have requirements to execute test commands in remote and host in coordinated manner, which is the motivation behind creating this framework.

Currently this framework supports,  following remote connection models.

1. SSH - Remote device is connected to host via WIFI or Ethernet cable.
2. ADB - Remote device is connected to host via USB (and supports ADB).
3. Serial - Remote device is connected to host via serial cable.
