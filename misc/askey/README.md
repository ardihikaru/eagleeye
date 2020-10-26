## Instruction how to use

### Requirements
- Two Computers in the same network, for example, `192.168.1.***`
- These two computers can ping each other
- Install python library based on `requirements.txt` file

### Scenario
- **Computer A** with IP: `192.168.1.2`, as extractor and sends frames
- **Computer B** with IP: `192.168.1.3`, as frames receiver

### How to use
1. Put `extractor.py` file into **Computer A**
2. Put `visualizer.py` file into **Computer B**
3. Run Visualizer file: `$ python3 visualizer.py --zmq-host "192.168.1.2"`
    - It assumes that **Computer A** acts as the sender (IP: `192.168.1.2`)
4. Run Extractor file: `$ python3 extractor.py --path "<your/desired/path>"`
    - If the input is a file: `$ python3 extractor.py --path "./video/eagleeye-sample.mp4"`
    - If the input is a URL: `$ python3 extractor.py --path "rtsp://localhost/test"`
    - If the input is a webcam (i.e. `0`): `$ python3 extractor.py --path "0"`
