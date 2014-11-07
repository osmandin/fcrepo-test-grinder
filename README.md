This is the Fedora load-testing framework for stress test with Grinder integration.
For information regarding Grinder, see [Grinder - Getting Started](http://grinder.sourceforge.net/g3/getting-started.html).

Installing Grinder
------------------

Prerequisites:  Jython 2.5.3, Java SE 7+

1. Download and install Jython
```bash
    $ curl http://search.maven.org/remotecontent?filepath=org/python/jython-installer/2.5.3/jython-installer-2.5.3.jar
    $ java -jar jython_installer-2.5.3.jar
```
    Set JYTHON_HOME environment variable:
```bash
    $ export JYTHON_HOME=</path/to/jython>
```

2. Download Grinder onto your launch host and unzip it
```bash
    $ curl http://sourceforge.net/projects/grinder/files/latest/download
```
	Set GRINDER_HOME and CLASSPATH environment variables for Grinder:
```bash
    $ export GRINDER_HOME=./grinder-3.11
    $ export CLASSPATH=$JYTHON_HOME/jython.jar:$GRINDER_HOME/lib/grinder.jar
```

3. Download and start the latest Fedora 4 release fcrepo-webapp-4.0.0-beta-04, or build it form [source](git@github.com:fcrepo4/fcrepo4.git) :
```bash
    $ curl https://github.com/fcrepo4/fcrepo4/releases/download/fcrepo-webapp-4.0.0-beta-04/fcrepo-webapp-4.0.0-beta-04-jetty-console.war
    $ java -jar fcrepo-webapp-4.0.0-beta-04-jetty-console.war
```

Setting up the tests
--------------------

The test scenario consists of, at a minimum, these two files:

* &lt;scenario&gt;.properties  
  See [The Grinder 3 Properties File] (http://grinder.sourceforge.net/g3/properties.html) for configuration.

* &lt;scenario&gt;.py  
  The actual test script written in Jython to performs the test.  

The **files** directory contains files that can be used for testing different ingest options:
single file, multiple files and mix files.

Running Grinder Manually
------------------------

Start up the console:
```bash
    $ export CLASSPATH=$JYTHON_HOME/jython.jar:$GRINDER_HOME/lib/grinder.jar
    $ java net.grinder.Console
```

Setting up the agent environment for ingest (mix file option, local deployed repository):
```bash
    $ export CLASSPATH=$JYTHON_HOME/jython.jar:$GRINDER_HOME/lib/grinder.jar    
    $ export INGEST_OPTION=mix
    $ export FCREPO_URL=http://localhost:8080/rest/
```

Start up your agents:
```bash
    $ cd src/scenarios/ingest    
    $ java net.grinder.Grinder ingest.properties
```
    
Once the agents contact the console, the start and reset icons on the console will be enabled. 
You may use the Action menu to control the tests:

* **Action->Collect Statistics**:  Start collection of statistics.
* **Action->Start Processes**:     Start the worker threads.
* **Action->Stop Processes**:      Stop the worker threads.


Grinder Output
-----------------------
Log files are located at src/scenarios/ingest.
See <http://grinder.sourceforge.net/g3/getting-started.html#Output> for more information.
