Whisperer
=========

![dw_logo](http://digitalwhisper.co.il/logo.png "DigitalWhisper Logo")

## Description
Tool for downloading [DigitalWhisper](http://digitalwhisper.co.il/) issues easily.

## Examples
##### Grab all issues

```
./whisperer.py -r all
```

##### Grab a range of issues

```
./whisperer.py -r 13-37 # Download issue 13 to 37
./whisperer.py -r 13-last # Download 13 to lastest issue
./whisperer.py -r 1,2-4,last # Download issues 1,2,3,4 and latest
```

##### Set download path

```
./whisperer.py -d ~/foo/bar
```
Defaults to current working directory


Enjoy reading!
