# Chord: Distributed Hash Table
* This project is an implementation of chord protocol. 
* The implementation is in python. 
* All the packages used come by default with python3.


## Code and Module Developers

#### Module Developers
1. chord: Adarsh Trivedi and Ishan Goel
2. client: Adarsh Trivedi
3. messaging: Adarsh Trivedi
4. performance: Adarsh Trivedi
5. test: Adarsh Trivedi
6. utilities: Adarsh Trivedi and Ishan Goel

#### Important functions developers

##### chord/node.py -- Node class 

1. join() - Ishan Goel and Adarsh Trivedi
2. init_finger_table() - Ishan Goel
3. update_others(), update_finger_table() - Ishan Goel and Adarsh Trivedi
4. find_successor(), find_predecessor() - Ishan Goel
5. closest_preceding_finger() - Ishan Goel
6. leave() - Adarsh Trivedi
7. set(), get(), delete() - Adarsh Trivedi
8. stabilization() - Adarsh Trivedi
9. Key transfer methods during join and leave- Adarsh Trivedi
10. Replication methods - Adarsh Trivedi

## Usage Guide

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

    Chord server can be started using chord_server.py module. Below is the complete description of
    how this module can be used to spawning chord servers.
    
    ```angular2
      python3.7 chord_server.py -h
      usage: chord_server.py [-h] --config CONFIG
                       [--bootstrap-server BOOTSTRAP_SERVER]
                       [--server-id SERVER_ID] [--no-hash]

      optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       Location to configuration file.
      --bootstrap-server BOOTSTRAP_SERVER
                            Bootstrap server in the form (localhost:5000).
      --server-id SERVER_ID
                            Server id on chord node. Use this only for testing
                            purpose.
      --no-hash             If provided requires keys to be stored to be
                            numeric.No hashing is performed on keys.
    ```
  
    Special Parameter Explanation:
    
    -  --server-id: If this parameter is provided, the program overrids
       the functionality of hashing ip:port to form server id and uses the
       value provided here.
       
    - --no-hash: If this parameter is set, then all the keys are expected to be
        integer as no hashing is performed on incoming query keys. This parameter is useful
        for debugging and testing.
        
    Start Nodes:
    
    - Starting a chord node without bootstrap server. This means creating a new chord ring.
        ```angular2
        cd chord-dht
        # assuming config.json is the configuration file
        python3.7 chord_server.py --config config.json
        ```
    - Starting a chord node with bootstrap server. This means joining an existing chord ring.
        ```angular2
        cd chord-dht
        # assuming config.json is the configuration file
        python3.7 chord_server.py --config config.json --bootstrap-server localhost:5001
        ```
    - Running multiple nodes on a single computer \[For testing out the things\]
        
        **[Sample configuration files can be found here.](config/)**
        
        ```angular2
        # Terminal Tab 1 [Running 1st chord node]
        # This would start a new chord node in a new ring. 
        # Since there is not bootstrap server.
        cd chord-dht
        python3.7 chord_server.py --config config1.json
        ```
      
        ```angular2
        # Terminal Tab 2
        # This would start a new chord node in an existing ring.
        # Assuming first node was configured to run on port 5001.
        cd chord-dht
        python3.7 chord_server.py --config config2.json --bootstrap-server localhost:5001
        ```

        ```angular2
        # Terminal Tab 3
        # This would start a new chord node in an existing ring.
        # Any of the below python commands work since there are two
        # nodes now in the ring on assumed ports 5001 or 5002.
        cd chord-dht
        python3.7 chord_server.py --config config2.json --bootstrap-server localhost:5001
        or
        python3.7 chord_server.py --config config2.json --bootstrap-server localhost:5002
        ```
      
    - CLI Tools to track current node states and perform debugging operations
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

## Test

#### Test Coverage

- The test cases cover 3 critical aspects of the implementation, which when correct ensure
accurate functioning of the system.
    - Successor and predecessor pointers correctness.
    - Stabilization correctness
- Pointers correctness ensure correct routing of the queries. Incorrect finger
table would cause more hop jumps but incorrect pointers would cause incorrect routing.
- Stabilization is important to maintain correct node pointers hence is  included for automated tests.

#### Dummy Nodes for tests

There is a module present to start dummy nodes which are used to perform tests. 
The dummy nodes are started on ports 5001-5005 on localhost. The module also gives control
to simulate joins, leaves and crashes of particular nodes out of the 5 nodes. User has to provide node ids
which will be assigned to these 5 dummy nodes.

- Usage
    
    ```angular2
    cd chord-dht
    PYTHONPATH=. python3.7 test/start_dummy_nodes.py test/config.test.json 100000 300000 500000 700000 900000
    ```
  
- Dummy Nodes console

    ```angular2
    PYTHONPATH=. python3.7 test/start_dummy_nodes.py test/config.test.json 100000 300000 500000 700000 900000
    Started node 1.
    Started node 2.
    Started node 3.
    Started node 4.
    Started node 5.
    1."stop" to stop dummy servers
    2."stop_i" to stop ith node
    3."node_i_id" Get ith node's id
    4."start_i" to start ith node
    5."crash_i" Crash i node
    Enter input:
    ```
  
- Stopping particular node

    ```angular2
    Enter input:stop_i
    Enter i value:4
    Retrying to stop node 4.
    Stopped dummy node 4.
    ```
  
- Restarting a stopped node

    ```angular2
    Enter input:start_i
    Enter i value:4
    Started node 4.
    ```

- Crashing a particual node

    ```angular2
    Enter input:crash_i
    Enter i value:4
    Retrying to stop node 4.
    Stopped dummy node 4.
    ```
  
- The console is to be used while running interactive test cases. For automated test cases just run the python command. There is no need 
for the console.
#### Test Interfaces
#####Two sets of testing interfaces are included namely automated and interactive.
- Automated Test Cases: 

    * No need to explicitly start dummy nodes for automated test. They are started automatically.
    * How to run automated test:
        ```angular2
        PYTHONPATH=./ python3.7 -m unittest discover -s test/ -p "*_automated_test.py"
        ```
      
    * Sample Run Output
    
        ```angular2
        Initializing dummy chord nodes with ids 100000, 300000, 500000, 700000, 900000.
        Started node 1.
        Started node 2.
        Started node 3.
        Started node 4.
        Started node 5.
        Testing predecessor pointers without leaves/failures.
        Checking predecessor of 100000. Should be 900000.
        Checking predecessor of 900000. Should be 700000.
        .Testing predecessor pointer updates/stabilization after node crash.
        Crashing node 5 [id 900000].
        Retrying to stop node 5.
        Stopped dummy node 5.
        Checking predecessor of node 1 [id 100000]. Should be 700000.
        Starting back node 5 [id 900000].
        Started node 5.
        .Testing predecessor pointer updates after graceful leaves.
        Stopping node 5 [id 900000].
        Retrying to stop node 5.
        Stopped dummy node 5.
        Checking predecessor of node 1 [id 100000]. Should be 700000.
        Starting back node 5 [id 900000].
        Started node 5.
        .Initializing dummy chord nodes with ids 100000, 300000, 500000, 700000, 900000.
        Started node 1.
        Started node 2.
        Started node 3.
        Started node 4.
        Started node 5.
        Testing successor pointers without leaves/failures.
        Checking successor of 100000. Should be 300000.
        Checking successor of 900000. Should be 100000.
        .Testing successor pointer updates/stabilization after node crash.
        Crashing node 5 [id 900000].
        Retrying to stop node 5.
        Stopped dummy node 5.
        [Errno 61] Connection refused
        [Errno 61] Connection refused
        Checking successor of node 4 [id 700000]. Should be 100000.
        Starting back node 5 [id 900000].
        Started node 5.
        .Testing successor pointer updates after graceful leaves.
        Stopping node 5 [id 900000].
        Retrying to stop node 5.
        Stopped dummy node 5.
        Checking successor of node 4 [id 700000]. Should be 100000.
        Starting back node 5 [id 900000].
        Started node 5.
        .
        ----------------------------------------------------------------------
        Ran 6 tests in 76.277s
        
        OK
        ```
      
- Interactive Tests

    * Start dummy nodes
        ```angular2
        cd chord-dht
        PYTHONPATH=. python3.7 test/start_dummy_nodes.py test/config.test.json 100000 300000 500000 700000 900000
        ```
    * Start automated tests
        ```angular2
        cd chord-dht
        PYTHONPATH=./ python3.7 -m unittest discover -s test/interactive_test/ -p "*_test.py"
        ```
      
    * Sample Output - Dummy Node Console
    
        ```angular2
        PYTHONPATH=. python3.7 test/start_dummy_nodes.py test/config.test.json 100000 300000 500000 700000 900000
        Started node 1.
        Started node 2.
        Started node 3.
        Started node 4.
        Started node 5.
        1."stop" to stop dummy servers
        2."stop_i" to stop ith node
        3."node_i_id" Get ith node's id
        4."start_i" to start ith node
        5."crash_i" Crash i node
        Enter input:crash_i
        Enter i value:5
        Retrying to stop node 5.
        Stopped dummy node 5.
        1."stop" to stop dummy servers
        2."stop_i" to stop ith node
        3."node_i_id" Get ith node's id
        4."start_i" to start ith node
        5."crash_i" Crash i node
        Enter input:start_i
        Enter i value:5
        Started node 5.
        1."stop" to stop dummy servers
        2."stop_i" to stop ith node
        3."node_i_id" Get ith node's id
        4."start_i" to start ith node
        5."crash_i" Crash i node
        Enter input:stop_i
        Enter i value:5
        Retrying to stop node 5.
        Stopped dummy node 5.
        1."stop" to stop dummy servers
        2."stop_i" to stop ith node
        3."node_i_id" Get ith node's id
        4."start_i" to start ith node
        5."crash_i" Crash i node
        Enter input:start_i
        Enter i value:5
        'NoneType' object is not subscriptable
        Started node 5.
        1."stop" to stop dummy servers
        2."stop_i" to stop ith node
        3."node_i_id" Get ith node's id
        4."start_i" to start ith node
        5."crash_i" Crash i node
        Enter input:crash_i
        Enter i value:2
        Retrying to stop node 2.
        Stopped dummy node 2.
        1."stop" to stop dummy servers
        2."stop_i" to stop ith node
        3."node_i_id" Get ith node's id
        4."start_i" to start ith node
        5."crash_i" Crash i node
        Enter input:start_i
        Enter i value:2
        Started node 2.
        1."stop" to stop dummy servers
        2."stop_i" to stop ith node
        3."node_i_id" Get ith node's id
        4."start_i" to start ith node
        5."crash_i" Crash i node
        Enter input:stop
        Retrying to stop node 5.
        Stopped dummy node 5.
        Stopped server 5.
        Retrying to stop node 4.
        Stopped dummy node 4.
        Stopped server 4.
        Retrying to stop node 3.
        sStopped dummy node 3.
        Stopped server 3.
        Retrying to stop node 2.
        Stopped dummy node 2.
        Stopped server 2.
        Retrying to stop node 1.
        Stopped dummy node 1.
        Stopped server 1.
        ```
      
    * Interactive Test Cases Output: Use above output to figure out how its working
    
     ```angular2
        PYTHONPATH=./ python3.7 -m unittest discover -s test/interactive_test/ -p "*_test.py"
        Testing predecessor pointers in normal scenario.
        Predecessor of [provide something like localhost:5001] or stop:localhost:5002
        Enter expected value:100000
        Testing predecessor pointers in normal scenario.
        Predecessor of [provide something like localhost:5001] or stop:localhost:5001
        Enter expected value:900000
        Testing predecessor pointers in normal scenario.
        Predecessor of [provide something like localhost:5001] or stop:stop
        .Testing predecessor pointers after crash.
        predecessor of [provide something like localhost:5001] or stop:localhost:5001
        Enter expected value:700000
        700000 [700000, 'localhost:5004']
        Testing predecessor pointers after crash.
        predecessor of [provide something like localhost:5001] or stop:stop
        .Testing predecessor pointers after leave scenario.
        predecessor of [provide something like localhost:5001] or stop:localhost:5001
        Enter expected value:700000
        Testing predecessor pointers after leave scenario.
        predecessor of [provide something like localhost:5001] or stop:stop
        .Testing successor pointers in normal scenario.
        Successor of [provide something like localhost:5001] or stop:localhost:5001
        Enter expected value:300000
        Testing successor pointers in normal scenario.
        Successor of [provide something like localhost:5001] or stop:stop
        .Testing successor pointers after crash.
        Successor of [provide something like localhost:5001] or stop:localhost:5001
        Enter expected value:500000
        Testing successor pointers after crash.
        Successor of [provide something like localhost:5001] or stop:stop
        .Testing successor pointers after leave scenario.
        Successor of [provide something like localhost:5001] or stop:stop
        .
        ----------------------------------------------------------------------
        Ran 6 tests in 160.013s
        
        OK
     ```

## Performance

#### Performance Scenarios Automated

Three performance parameters are automated for results comparisons.

1. Write performance with different sample sizes
2. Read vs Write performance comparison with different sample sizes
3. Write vs Node Count performance comparison with different sample sizes


#### Performance Framework

Performance scenarios can be run with performance/run.py script. Below is the help
output for the script along with some examples.

    PYTHONPATH=./ python3.7 performance/run.py -h
    usage: run.py [-h] --type {write,readwrite,nodecount}
                  [--input-file INPUT_FILE] --bootstrap-server BOOTSTRAP_SERVER
                  [--sample-size SAMPLE_SIZE] [--epochs-per-sample E_PER_SAMPLE]
                  [--display-performance-output] [--plot-performance-output]
    
    optional arguments:
      -h, --help            show this help message and exit
      --type {write,readwrite,nodecount}
                            Type of performance testing. Valid values ['write',
                            'readwrite', 'nodecount'].
      --input-file INPUT_FILE
                            Input file to pick data to store on chord.
      --bootstrap-server BOOTSTRAP_SERVER
                            Any running chord server in format localhost:5000.
      --sample-size SAMPLE_SIZE
                            Sample sizes to run performance against.
      --epochs-per-sample E_PER_SAMPLE
                            Number of epochs to run per sample size.
      --display-performance-output
                            Set to print the performance output.
      --plot-performance-output
                            Set to display the performance output as plot.
                            
                            
Sample Run Example:

    PYTHONPATH=./ python3.7 performance/run.py 
    --input-file performance/sample.txt 
    --bootstrap-server localhost:5001 
    --type nodecount 
    --sample-size 10 --sample-size 25 --sample-size 50 
    --display-performance-output 
    --plot-performance-outpu
