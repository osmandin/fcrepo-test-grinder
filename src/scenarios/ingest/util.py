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
from HTTPClient import NVPair

fullBaseURL = os.environ.get('FCREPO_URL', 'http://localhost:8080/rest/')

class Util:
    # Identify the running thread for logging
    THREAD_NUM = 0
    LOCK = Lock()

    requestUrl = ''
    threadNum = 0

    def __init__(self):
        Util.LOCK.acquire()
        try:
            Util.THREAD_NUM += 1
            self.threadNum = Util.THREAD_NUM
        finally:
            Util.LOCK.release()


    # Create object resource to hole the test files.

    # Grinder HTTPRequest will always POST multipart/form requests, with
    # which the fcrepo will create empty binary contents instead of objects.
    # Manipulate with httplib to walk around it.
    def create(self):
        oid = str(uuid.uuid4())
        self.requestUrl = urljoin(fullBaseURL, oid)

        paths = self.requestUrl.split("/", 3)
        conn = httplib.HTTPConnection(paths[2])
        conn.request("PUT", "/" + paths[3])
        response = conn.getresponse()
        print "\nThread #" + str(
        self.threadNum) + " created object: " + self.requestUrl, response.status, response.reason
        conn.close()
        return oid
