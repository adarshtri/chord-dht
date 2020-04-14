# Chord: Distributed Hash Table
* This project is an implementation of chord protocol. 
* The implementation is in python. 
* There is no external dependency required. 
* All the packages used come by default with python3.

### Usage Guide

- Clone the [repository](https://github.com/adarshtri/chord-dht.git)

    ```git clone https://github.com/adarshtri/chord-dht.git```
    
- Configure a chord node:
  
  To run a chord server we need a configuration file with certain properties.
  Here is a sample content of a configuration file with properties
  explanation.
    
    ```
  {
  "ip": "localhost",
  "advertised_ip": "",
  "socket_port": 5001,
  "m_bits": 20,
  "stabilize_interval": 2,
  "log_file": "logs/chord1/chord.log",
  "log_to_console": 0,
  "log_frequency_interval": 5,
  "log_frequency_unit": "m",
  "log_frequency_backup_count": 10000
    }
  ```
  Properties explanation:
  - ip: For trying it out use "localhost".
  - advertised_ip: Should be left blank. A blank value implies node can be connected either by ip address or hostname or any other possible way. Specifying a value restricts connection only through that way.
  - socket_port: Port on which the server would run.
  - m_bit: Number of bits used from the consistent hashing. Decides the size of the chord ring. Try to keep it consistent across all the peers.
  - stabilize_interval: After how many seconds the stabilization protocol should trigger.
  - Logging properties: Should be understandable from the naming convention.
  
- Running chord server:
    - Starting a chord node without bootstrap server. This means creating a new chord ring.
        ```angular2
        cd chord-dht
        # assuming config.json is the configuration file
        python3.7 chord_server.py config.json
        ```
    - Starting a chord node with bootstrap server. This means joining an existing chord ring.
        ```angular2
        cd chord-dht
        # assuming config.json is the configuration file
        python3.7 chord_server.py config.json localhost:5001
        ```
    - Running multiple nodes on a single computer \[For testing out the things\]
        
        **[Sample configuration files can be found here.](config/)**
        
        ```angular2
        # Terminal Tab 1 [Running 1st chord node]
        # This would start a new chord node in a new ring. 
        # Since there is not bootstrap server.
        cd chord-dht
        python3.7 chord_server.py config1.json
        ```
      
        ```angular2
        # Terminal Tab 2
        # This would start a new chord node in an existing ring.
        # Assuming first node was configured to run on port 5001.
        cd chord-dht
        python3.7 chord_server.py config2.json localhost:5001
        ```

        ```angular2
        # Terminal Tab 2
        # This would start a new chord node in an existing ring.
        # Any of the below python commands work since there are two
        # nodes now in the ring on assumed ports 5001 or 5002.
        cd chord-dht
        python3.7 chord_server.py config2.json localhost:5001
        or
        python3.7 chord_server.py config2.json localhost:5002
        ```
      
    - CLI Tools to track current node state
        - Upon running the server multiple command line options are provided to track the running node.
        - Sample CLI Window
            ```angular2
            python chord_server.py config/config1.json 
    
            Running with server id : 1004174
            1. "stop" to shutdown chord node
            2. "reset" to reload new configuration
            3. "pred" Get predecessor
            4. "succ" Get successor
            5. "ftable" Finger Table
            6. "store" Store
            7. "ssize" Store Size
            8. "set" Set a key
            9. "get" Get a key location
            10. "del" Delete a key
            Enter your input:
            ```
        - Options are self explanatory.
 
- The Client Library 

    ```angular2
    from client.chord_client import ChordClient
  
    # create a new client by connecting to one of the peers.
    client = ChordClient(bootstrap_server="localhost:5004")
  
    # set, get and delete a key from the p2p system.
    # All the client methods return the node details on which the key was store.
    client.store("chord")
    client.get("chord")
    client.delete("chord")
    ```
- Handling server in a custom way

    - The chord server is implemented as a "Node" class in package "chord" and module "node".
    - You can create multiple chord server by creating instance of this class.
    - chord_server.py is a good starting point of how to handle the instance of this class.
    - Currently the instance of Node class is non blocking. So after it's creation there has to be something blocking.
    Like an infinite loop.
    - The Node instance is also passed to an XMLRPC server for registration. XMLRPC is used for inter-node communication
    in this implementation.
    - We aim to improve ways in which this class can be made more seamless with added functionalities of server creation.
