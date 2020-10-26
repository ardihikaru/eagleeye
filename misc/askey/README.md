## Instruction how to use

### Requirements
- Two Computers in the same network, for example, `192.168.1.***`
- These two computers can ping each other
- Install python library based on `requirements.txt` file

### Scenario
- **Computer A** with IP: 192.168.1.2
- **Computer B** with IP: 192.168.1.3

### How to use
1. Put `extractor.py` file into **Computer A**
2. Put `visualizer.py` file into **Computer B**
3. Run Visualizer file: `$ python3 visualizer.py`
4. Run Extractor file: `$ python3 extractor.py --path "<your/desired/path>"`
    - If the input is a
