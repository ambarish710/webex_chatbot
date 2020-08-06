import json
import logging
import ruamel.yaml
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GenericWrappper:
    """
        Generic Wrapper Class which contains helper methods and other
        required generic variables
    """
    def __init__(self):
        """
            Init Method
            Declaring constants and creating logger object
        """
        self.logger = logging.getLogger('chatbot_logger')
        self.yaml = ruamel.yaml.YAML()
        self.proxies = {}
        with open('information.yaml', 'r') as ifh:
            doc = self.yaml.load(ifh)
            self.proxies["http"] = str(doc["general_details"]["http_proxy"])
            self.proxies["https"] = str(doc["general_details"]["https_proxy"])
            self.proxy_flag = str(doc["general_details"]["proxy"])
        self.HELP_TEXT = """Keywords (with examples):
        [Keywords are case insensitive]
        Bug details:                    Gives a brief description for the given BUG-ID
                                        \t\t@BUG_NOTIFIER_BOT get bug details: BUG-ID
                                        \t\t@BUG_NOTIFIER_BOT get bug details: MAGLEV-6347

        Last promoted build:            Gives last promoted build for a given branch
                                        \t\t@BUG_NOTIFIER_BOT get last promoted build BRANCH
                                        \t\t@BUG_NOTIFIER_BOT get last promoted build 1.4.0

        Current build:                  Gives current build for a given branch
                                        \t\t@BUG_NOTIFIER_BOT get current build BRANCH
                                        \t\t@BUG_NOTIFIER_BOT get current build 1.3.0

        Testing status:                 Gives overall testing status for a given build
                                        \t\t@BUG_NOTIFIER_BOT get testing status: COMPONENT BUILD-ID
                                        \t\t@BUG_NOTIFIER_BOT get testing status: Maglev 1.3.0.100

        Detailed testing status:        Gives detailed status of each regression job for a given build
                                        \t\t@BUG_NOTIFIER_BOT get detailed testing status: COMPONENT BUILD-ID
                                        \t\t@BUG_NOTIFIER_BOT get detailed testing status: Maglev 1.3.0.100

        Troubleshoot cluster:           Runs a set of troubleshooting commands on given cluster and provide status in personal chat
                                        \t\t@BUG_NOTIFIER_BOT troubleshoot HOSTNAME SSH_USERNAME SSH_PASSWORD MAGLEV_USERNAME MAGLEV_PASSWORD
                                        \t\t@BUG_NOTIFIER_BOT troubleshoot 10.198.198.1 maglev maglev1@3 admin maglev1@3

        Add New Keyword:                Adds new keyword to query mapping
                                        \t\t@BUG_NOTIFIER_BOT Add Keyword > KEYWORD : JIRA QUERY
                                        \t\t@BUG_NOTIFIER_BOT Add Keyword > Open DNAC1.5 Bugs : type = Bug AND labels = dnac15-mf

        Delete Existing Keyword:        Deletes existing keyword to query mapping
                                        \t\t@BUG_NOTIFIER_BOT Delete Keyword > KEYWORD : JIRA QUERY
                                        \t\t@BUG_NOTIFIER_BOT Delete Keyword > Open DNAC1.5 Bugs : type = Bug AND labels = dnac15-mf
        \n"""


    def update_timestamp(self, metadata, updated_time):
        """
            Update last served request timestamp in
            tmp/metadata.yaml
            :param metadata: Timestamp
        """
        self.logger.info("Updating tmp/metadata.yaml...")
        self.logger.info("With last served request timestamp")
        metadata["read_only"]["last_served_request"] = updated_time
        with open('tmp/metadata.yaml', 'w') as mfh:
            self.yaml.dump(metadata, mfh)
        self.logger.info("Successfully updated tmp/metadata.yaml!!!")


    def get_token(self):
        """
            Get token from metadata.yaml file and return it
            :return: X-Auth-Token for QDNA server
        """
        self.logger.info("Accessing QDNA token from tmp/metadata.yaml...")
        with open('tmp/metadata.yaml', 'r') as mfh:
            metadata = self.yaml.load(mfh)
            token = str(metadata['read_only']['qdna_server_token'])
            self.logger.info("Successfully accessed token from tmp/metadata.yaml!!!")
            return token


    def set_token(self, token):
        """
            Set X-Auth-Token for QDNA server to metadata.yaml file
        """
        self.logger.info("Updating QDNA token in tmp/metadata.yaml...")
        with open('tmp/metadata.yaml', 'r') as mfh:
            metadata = self.yaml.load(mfh)
        metadata['read_only']['qdna_server_token'] = str(token)
        with open('tmp/metadata.yaml', 'w') as mfh:
            self.yaml.dump(metadata, mfh)
        self.logger.info("Successfully updated QDNA token")


    def requests_post(self, url, data=None, headers=None,
                      auth=None, verify=False, do_not_set_proxy=False):
        """
            POST API CALL
            :param url: URL
            :param data: Data to pass with the URL
            :param headers: Headers to pass with the URL
            :param auth: Username and password credentials
            :param verify: Verify value
            :param do_not_set_proxy: Set it to true, if you don't want to use
                                     proxy for certain API calls
            :return:     Returns output recieved from the POST API call
        """
        self.logger.info("POST API CALL")
        self.logger.info("URL: {}".format(url))
        self.logger.info("Data: {}".format(data))
        self.logger.info("Authentication Headers: {}".format(headers))
        self.logger.info("Proxy Flag: {}".format(self.proxy_flag))
        self.logger.info("Proxies: {}".format(self.proxies))
        self.logger.info("do_not_set_proxy flag: {}".format(do_not_set_proxy))
        try:
            if self.proxy_flag.lower() == 'true' and auth != None and do_not_set_proxy == False:
                self.logger.info("Using proxy for the following POST API call...")
                output = requests.post(url=url, verify=verify,
                                       proxies=self.proxies, auth=auth,
                                       timeout=5)
            elif self.proxy_flag.lower() == 'true' and auth == None and do_not_set_proxy == False:
                self.logger.info("Using proxy for the following POST API call...")
                output = requests.post(url=url, headers=headers,
                                       verify=verify,
                                       data=json.dumps(data),
                                       proxies=self.proxies, auth=auth,
                                       timeout=5)
            elif self.proxy_flag.lower() == 'false' and auth != None and do_not_set_proxy == False:
                self.logger.info("Not using proxy for the following POST API call...")
                output = requests.post(url = url, verify = verify,
                                       auth = auth, timeout=5)
            elif self.proxy_flag.lower() == 'false' and auth == None and do_not_set_proxy == False:
                self.logger.info("Not using proxy for the following POST API call...")
                output = requests.post(url=url, headers=headers,
                                       verify=verify,
                                       data=json.dumps(data), timeout=5)
            elif do_not_set_proxy == True and auth != None:
                self.logger.info("Not using proxy for the following POST API call...")
                output = requests.post(url=url, verify=verify,
                                       auth=auth, timeout=5)
            elif do_not_set_proxy == True and auth == None:
                self.logger.info("Not using proxy for the following POST API call...")
                output = requests.post(url=url, headers=headers,
                                       verify=verify,
                                       data=json.dumps(data), timeout=5)
            self.logger.info("Output: {}".format(output))
            return output
        except Exception as e:
            self.logger.error("Error: {}".format(e))


    def requests_get(self, url, headers=None, verify=False, do_not_set_proxy=False):
        """
            GET API CALL
            :param url: URL
            :param headers: Headers to pass with the URL
            :param verify: Verify value
            :param do_not_set_proxy: Set it to true, if you don't want to use
                                     proxy for certain API calls
            :return:     Returns output recieved from the GET API call
        """
        self.logger.info("GET API CALL")
        self.logger.info("URL: {}".format(url))
        self.logger.info("Authentication Headers: {}".format(headers))
        self.logger.info("Proxy Flag: {}".format(self.proxy_flag))
        self.logger.info("Proxies: {}".format(self.proxies))
        self.logger.info("Verify: {}".format(verify))
        self.logger.info("do_not_set_proxy flag: {}".format(do_not_set_proxy))
        try:
            if self.proxy_flag.lower() == 'true' and do_not_set_proxy == False:
                self.logger.info("Using proxy for the following GET API call...")
                output = requests.get(url = url, verify = verify,
                                      headers = headers, proxies = self.proxies,
                                      timeout=8)
            else:
                self.logger.info("Not using proxy for the following GET API call...")
                output = requests.get(url = url, verify = verify,
                                      headers = headers, timeout=8)
            self.logger.info("Output: {}".format(output))
            return output
        except Exception as e:
            self.logger.error("Error: {}".format(e))
