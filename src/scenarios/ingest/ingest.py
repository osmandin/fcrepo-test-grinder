# Copyright 2014 DuraSpace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import string
import os
import uuid
import mimetypes
import httplib, urllib
from threading import Lock
import java.io as io
import org.python.util as util

from urlparse import urljoin
from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from net.grinder.plugin.http import HTTPRequest
from HTTPClient import NVPair

# Ingest scenario options (single, multiple, mix) with files placed in each folder
option = os.environ.get('INGEST_OPTION', 'single')
# Fedora repository Url, default http://localhost:8080/rest/
fullBaseURL = os.environ.get('FCREPO_URL', 'http://localhost:8080/rest/')
# Test file(s) location
filesDir = 'files/' + option + '/'
test1 = Test(1, "File Ingest Test")

request1 = test1.wrap(HTTPRequest())
# Instrument the request with Test
test1.record(request1)

#
# TestRunner test ingest files in directory /files with scenario/
# options for single file, multiple files, and mix files.
#
# @author lsitu
# @since  11/06/2014
#
class TestRunner:

    # Identify the running thread for logging
    THREAD_NUM = 0
    LOCK = Lock()

    requestUrl = ''
    threadNum = 0

    # The __init__ method is called once for each thread.
    # Put any test thread initializations here
    def __init__(self):

        # Assigning the thread ID
        TestRunner.LOCK.acquire()
        try:
             TestRunner.THREAD_NUM += 1
             self.threadNum = TestRunner.THREAD_NUM
        finally:
            TestRunner.LOCK.release()

        # Create object resource to hole the test files.
        # 
        # Grinder HTTPRequest will always POST multipart/form requests, with 
        # which the fcrepo will create empty binary contents instead of objects.
        # Manipulate with httplib to walk aroung it.
        #
        oid = str(uuid.uuid4())
        self.requestUrl = urljoin( fullBaseURL, oid )

        paths = self.requestUrl.split( "/", 3 )
        conn = httplib.HTTPConnection(paths[2])
        conn.request( "PUT", "/" + paths[3] )
        response = conn.getresponse()
        print "\nThread #" + str(self.threadNum) + " created object: " + self.requestUrl, response.status, response.reason
        conn.close()



    # The __call__ method is called for each test run performed by
    # a worker thread.
    def __call__(self):

        print "Ingest files directory: " + filesDir
        # Don't report to the cosole until we verify the result
        grinder.statistics.delayReports = 1
        
        # Ingest all the files one by one in directory $filesDir
        for f in os.listdir(filesDir):
            # Skit those hidden files like .DS_Store
            if ( f.startswith('.') == False ):
                cType, encoding = mimetypes.guess_type(f)
                if cType is None or encoding is not None:
                    cType = 'application/octet-stream'
                headers = ( NVPair( "Content-Type", cType ), )

                inFile = io.FileInputStream(filesDir + f)

                # Call the version of POST that takes a byte array.
                result = request1.POST( self.requestUrl, inFile, headers )
                print "\nThread #" + str(self.threadNum) + " ingested " + f + ": " + self.requestUrl + " " + str(result.statusCode)
                inFile.close();

                if result.statusCode == 201:
    	           # Report to the console
    	           grinder.statistics.forLastTest.setSuccess(1)
                else:
    	           print "\nThread #" + str(self.threadNum) + " error: POST " + self.requestUrl + " " + str(result.statusCode)

    # The __del__ method is called at shutdown once for each thread
    # It is useful for closing resources (e.g. database connections)
    # that were created in __init__.
    #def __del__(self):
