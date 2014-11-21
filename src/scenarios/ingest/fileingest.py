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
from util import *

# Ingest scenario options (single, multiple, mix) with files placed in each folder
option = os.environ.get('INGEST_OPTION', 'single')
# Fedora repository Url, default http://localhost:8080/rest/
fullBaseURL = os.environ.get('FCREPO_URL', 'http://localhost:8080/rest/')

# Init tests
test = Test(1, "Simple Ingest Small File")
request = test.wrap(HTTPRequest())
test.record(request)
dir = 'files/single/'

class TestRunner (Util):
    # Identify the running thread for logging
    THREAD_NUM = 0
    LOCK = Lock()

    threadNum = 0

    def __init__(self):
        TestRunner.LOCK.acquire()
        try:
            TestRunner.THREAD_NUM += 1
            self.threadNum = Util.THREAD_NUM
        finally:
            TestRunner.LOCK.release()


    def test_ingest(self, request, dir):
        oid = Util.create(self)
        request_url = fullBaseURL + oid

        grinder.statistics.delayReports = 1

        for f in os.listdir(dir):
            if not f.startswith('.'):
                filetype, encoding = mimetypes.guess_type(f)

                if filetype is None or encoding is not None:
                    filetype = 'application/octet-stream'

                headers = ( NVPair("Content-Type", filetype), )
                file_instream = io.FileInputStream(dir + f)
                result = request.POST(request_url, file_instream, headers)

                print "\nThread #" + str(self.threadNum) + " ingested " + f + ": " + self.requestUrl + " " + str(
                    result.statusCode)
                file_instream.close()

                if result.statusCode == 201:
                    grinder.statistics.forLastTest.setSuccess(1)
                else:
                    print "\nThread #" + str(self.threadNum) + " error: POST " + self.requestUrl + " " + str(
                        result.statusCode)


    def __call__(self):
        filetest = TestRunner()
        filetest.test_ingest(request, dir)