# Copyright 2014 DuraSpace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
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

# Init tests

test1 = Test(1, "Simple Ingest Small File")
simple_ingest_request_1 = test1.wrap(HTTPRequest())
test1.record(simple_ingest_request_1)
filesDir1 = 'files/simple-small/'

test2 = Test(2, "Simple Ingest Medium File")
simple_ingest_request_2 = test2.wrap(HTTPRequest())
test2.record(simple_ingest_request_2)
filesDir2 = 'files/simple-medium/'

test3 = Test(3, "Simple Ingest Large Files")
simple_ingest_request_3 = test3.wrap(HTTPRequest())
test3.record(simple_ingest_request_3)
filesDir3 = 'files/simple-large'

#...

test4 = Test(4, "Bulk Ingest Small File")
bulk_ingest_request_1 = test4.wrap(HTTPRequest())
test4.record(bulk_ingest_request_1)
filesDir4 = 'files/bulk-small/'

#...

test5 = Test(5, "Simple Access Small Files")
simple_access_request_1 = test5.wrap(HTTPRequest())
test5.record(simple_access_request_1)
filesDir5 = 'files/simple-small'

#...

test6 = Test(6, "Bulk Access Small Files")
bulk_access_request_6 = test6.wrap(HTTPRequest())
test6.record(bulk_access_request_6)
filesDir6 = 'files/bulk-small/'

class TestRunner:
    # Identify the running thread for logging
    THREAD_NUM = 0
    LOCK = Lock()

    requestUrl = ''
    threadNum = 0

    def __init__(self):
        TestRunner.LOCK.acquire()
        try:
            TestRunner.THREAD_NUM += 1
            self.threadNum = TestRunner.THREAD_NUM
        finally:
            TestRunner.LOCK.release()

        # Create object resource to hole the test files.
        # Grinder HTTPRequest will always POST multipart/form requests, with
        # which the fcrepo will create empty binary contents instead of objects.
        # Manipulate with httplib to walk aroung it.

        oid = str(uuid.uuid4())
        self.requestUrl = urljoin(fullBaseURL, oid)

        paths = self.requestUrl.split("/", 3)
        conn = httplib.HTTPConnection(paths[2])
        conn.request("PUT", "/" + paths[3])
        response = conn.getresponse()
        print "\nThread #" + str(
            self.threadNum) + " created object: " + self.requestUrl, response.status, response.reason
        conn.close()

    def test_ingest(self, request, dir):
        grinder.statistics.delayReports = 1

        for f in os.listdir(dir):
            if not f.startswith('.'):
                filetype, encoding = mimetypes.guess_type(f)

                if filetype is None or encoding is not None:
                    filetype = 'application/octet-stream'
                headers = ( NVPair("Content-Type", filetype), )
                file_instream = io.FileInputStream(dir + f)
                result = request.POST(self.requestUrl, file_instream, headers)
                print "\nThread #" + str(self.threadNum) + " ingested " + f + ": " + self.requestUrl + " " + str(
                    result.statusCode)
                file_instream.close()

                if result.statusCode == 201:
                    grinder.statistics.forLastTest.setSuccess(1)
                else:
                    print "\nThread #" + str(self.threadNum) + " error: POST " + self.requestUrl + " " + str(
                        result.statusCode)

    def test_access(self, request, dir):
        grinder.statistics.delayReports = 1

        for f in os.listdir(dir):
            if not f.startswith('.'):
                filetype, encoding = mimetypes.guess_type(f)

                if filetype is None or encoding is not None:
                    filetype = 'application/octet-stream'
                headers = ( NVPair("Content-Type", filetype), )
                file_instream = io.FileInputStream(dir + f)
                result = request.POST(self.requestUrl, file_instream, headers)
                print "\nThread #" + str(self.threadNum) + " ingested " + f + ": " + self.requestUrl + " " + str(
                    result.statusCode)
                file_instream.close()

                url = result.getHeader('Location')

                if result.statusCode == 201:
                    grinder.statistics.forLastTest.setSuccess(1)
                else:
                    print "\nThread #" + str(self.threadNum) + " error: POST " + self.requestUrl + " " + str(
                        result.statusCode)

                #confirm existence of file
                response = request.GET(url)
                response_status = response.statusCode
                size = response.data

                if response_status == 200:
                    print "\nThread #" + str(self.threadNum) + " OK: GET " + url + " FILE LENGTH: " + str(len(size))
                    grinder.statistics.forLastTest.setSuccess(1)
                else:
                    print "\nThread #" + str(self.threadNum) + "error: GET" + url + " " + str(response_status)


    def __call__(self):
        self.test_ingest(simple_ingest_request_1, filesDir1)
        self.test_ingest(simple_ingest_request_2, filesDir2)
        self.test_ingest(simple_ingest_request_3, filesDir3)
        self.test_access(bulk_ingest_request_1, filesDir4)
        #...
        self.test_access(simple_access_request_1, filesDir5)
        self.test_access(bulk_access_request_6, filesDir6)