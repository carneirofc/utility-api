utility-api
================

Webserver containing usefull APIs for Sirius CONS.

Spreadsheet
-----------

|Endpoint|Desc|Parameters|
|:------:|:--:|:--------:|
|`/devices?type="type"`|Get a json containing all devices of the requested type| One of the supported types|
|`/reload`|Reload the content in the spreadsheet, this is done automatically by the websever|||

|Supported Types|
|:-------------:|
| agilent|
|mks|

