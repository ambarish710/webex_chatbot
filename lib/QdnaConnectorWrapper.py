import json
import logging
from GenericWrappper import GenericWrappper



class QdnaConnectorWrapper:
    """
        QDNA Connector Wrapper Class containing helper methods
    """
    def __init__(self, cluster_ip, username, password):
        """
            Init Method
            :param cluster_ip: Cluster IP
            :param username: Username
            :param password: Password
        """
        self.generic_wrapper = GenericWrappper()
        self.cluster_ip = cluster_ip
        self.username = username
        self.password = password
        self.logger = logging.getLogger('chatbot_logger')
        self.url_request_header = {'content-type': 'application/json'}
        self.get_token_url = "https://{}/api/system/v1/identitymgmt/token".format(cluster_ip)
        self.build_status_url = 'https://{}/api/qdna/v1/dashboard/dashboardapi/apic/products'.format(cluster_ip)
        self.url_request_header['X-Auth-Token'] = self.generic_wrapper.get_token()


    def create_build_status_url(self, project, build_id):
        """
            Create build status url
            :param project: Project
            :param build_id: Build to monitor
            :return: build statistics in string format
        """
        build_prefix = float(build_id[:3])
        # Handling pipeline versioning change from 3 digit to 2 digits
        # Hoping newer releases follow the same 2 digit pattern now onwards
        # Else need to update the logic
        if build_prefix <= 1.4:
            build_status_url = str(self.build_status_url) + \
                               "/%s/branches/%s%%5B%s%%5D/versions/%s" % \
                               (project.upper(), project.capitalize(),
                                build_id[:5], build_id)
        else:
            build_status_url = str(self.build_status_url) + \
                               "/%s/branches/%s%%5B%s%%5D/versions/%s" % \
                               (project.upper(), project.capitalize(),
                                build_id[:3], build_id)
        detailed_build_status_url = build_status_url + "/components"
        return build_status_url, detailed_build_status_url


    def get_token(self):
        """
            Method to get token for the given cluster
            :return: Maglev cluster token
        """
        try:
            self.logger.info("---***--- Getting maglev token for {} ---***---".format(self.cluster_ip))
            self.logger.info("Identity management get token URL: {}".format(self.get_token_url))
            self.logger.info("Username: {}".format(self.username))
            self.logger.info("Password: {}".format(self.password))
            output = self.generic_wrapper.requests_post(url=self.get_token_url,
                                                        auth=(self.username, self.password),
                                                        do_not_set_proxy=True)
            self.logger.info("Ouput Response Code: {}".format(output))
            self.logger.info("Response: {}".format(output.content))
            json_response = json.loads(output.content)
            token = json_response['Token']
            self.logger.info("TOKEN: {}".format(token))
            self.url_request_header['X-Auth-Token'] = str(token)
            # Chat Bot Utility specific requirements (Can be removed)
            self.generic_wrapper.set_token(str(token))
        except Exception as e:
            self.logger.error("Failure in getting token,\nError -- {}".format(e))


    def formulate_testing_status_output(self, build_id, output):
        """
            Get output content and formulate return text
            :return: build statistics in string format
        """
        return_text = "{} Testing Status --\n".format(build_id)
        json_response = json.loads(output.content)
        for element in json_response["Versions"]:
            for entity in element:
                if "Score" in entity:
                    return_text += "\t" + "{}: {} %".format("Pass Percentage", str(element[entity])) + "\n"
                elif "TrackingID" in entity or "VersionDetails" in entity:
                    pass
                else:
                    return_text += "\t" + "{}: {}".format(str(entity), str(element[entity])) + "\n"
        build_prefix = float(build_id[:3])
        if build_prefix <= 1.4:
            return_text += "\nAdditional details can be found here -- " \
                           "https://qdna.cisco.com/builds/{}/MAGLEV/Maglev[{}]/{}"\
                           .format(build_id[:5], build_id[:5], build_id)
        else:
            return_text += "\nAdditional details can be found here -- " \
                           "https://qdna.cisco.com/builds/{}/MAGLEV/Maglev[{}]/{}"\
                           .format(build_prefix, build_prefix, build_id)
        self.logger.info("Return text: {}".format(return_text))
        return return_text


    def formulate_detailed_testing_status_output(self, build_id, output):
        """
            Get detailed status output and formulate return text
            :return: build statistics in string format
        """
        return_text = "{} Detailed Testing Status --\n".format(build_id)
        json_response = json.loads(output.content)
        for entity in json_response['Components']:
            self.logger.info("\t{} -- Total Tests - {}, Pass Percentage - {} %, Failures - {}\n"
                             .format(entity['ComponentName'], entity['TotalTests'],
                                     entity['Score'], entity['TotalFails']))
            return_text += "\t{} -- Total Tests - {}, Pass Percentage - {} %, Failures - {}\n"\
                            .format(entity['ComponentName'], entity['TotalTests'],
                                    entity['Score'], entity['TotalFails'])
            if len(entity['TestSuiteList']) > 1:
                for ts in entity['TestSuiteList']:
                    self.logger.info("\t\t{} -- Total Tests - {}, Pass Percentage - {} %, Failures - {}\n"
                                     .format(ts['TestSuiteName'], ts['TotalTests'],
                                             ts['Score'], ts['TotalFails']))
                    return_text += "\t\t{} -- Total Tests - {}, Pass Percentage - {} %, Failures - {}\n"\
                                     .format(ts['TestSuiteName'], ts['TotalTests'],
                                             ts['Score'], ts['TotalFails'])
        self.logger.info("Return text: {}".format(return_text))
        return return_text


    def get_testing_status_from_qdna(self, project, build_id):
        """
            Get overall testing status for a given build in a project and
            return text ouput
            :param project: Project
            :param build_id: Build ID
            :return: Build statistics
        """
        build_status_url, detailed_build_status_url = self.create_build_status_url(project, build_id)
        self.logger.info("Get build status final URL: {}".format(build_status_url))
        self.logger.info("Header: {}".format(self.url_request_header))
        output = self.generic_wrapper.requests_get(url=build_status_url,
                                                   headers=self.url_request_header,
                                                   do_not_set_proxy=True)
        self.logger.info("Ouput Response Code: {}".format(output))
        self.logger.info("Response: {}".format(output.content))
        if "token expired" in output.content or "Unauthorized" in output.content:
            self.get_token()
            output = self.generic_wrapper.requests_get(url=build_status_url,
                                                       headers=self.url_request_header,
                                                       do_not_set_proxy=True)
            return_text = self.formulate_testing_status_output(build_id=build_id, output=output)
        elif "200" in str(output):
            return_text = self.formulate_testing_status_output(build_id=build_id, output=output)
        else:
            return_text = "Error getting status from QDNA"
        return return_text


    def get_detailed_testing_status_from_qdna(self, project, build_id):
        """
            Get overall testing status for a given build in a project and
            return text ouput
            :param project: Project
            :param build_id: Build ID
            :return: Build statistics
        """
        build_status_url, detailed_build_status_url = self.create_build_status_url(project, build_id)
        self.logger.info("Get detailed build status final URL: {}".format(detailed_build_status_url))
        self.logger.info("Header: {}".format(self.url_request_header))
        output = self.generic_wrapper.requests_get(url = detailed_build_status_url,
                                                   headers = self.url_request_header,
                                                   do_not_set_proxy=True)
        self.logger.info("Ouput Response Code: {}".format(output))
        self.logger.info("Response: {}".format(output.content))
        if "token expired" in output.content or "Unauthorized" in output.content:
            self.get_token()
            output = self.generic_wrapper.requests_get(url = detailed_build_status_url,
                                                       headers = self.url_request_header,
                                                       do_not_set_proxy=True)
            self.logger.info("Ouput Response Code: {}".format(output))
            self.logger.info("Response: {}".format(output.content))
            return_text = self.formulate_detailed_testing_status_output(build_id=build_id, output=output)
        elif "200" in output:
            return_text = self.formulate_detailed_testing_status_output(build_id=build_id, output=output)
        else:
            return_text = "Error getting status from QDNA"
        return return_text
