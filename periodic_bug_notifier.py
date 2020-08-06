import yaml
import logging

from lib.GenericWrappper import GenericWrappper
from lib.JiraConnectionWrapper import JiraConnectionWrapper
from lib.WebexNotifierWrapper import WebexNotifierWrapper



class BugNotifierUtility:
    def __init__(self):
        """
            Initializes and sets variables by collecting metadata
            from information.yaml
        """

        self.generic_wrapper = GenericWrappper()
        self.webex_wrapper = WebexNotifierWrapper()
        self.jira_wrapper = JiraConnectionWrapper()
        self.logger = logging.getLogger('chatbot_logger')
        self.logger.info("Periodic Bug Notifier, Initializing...")
        self.webex_auth_headers = {'content-type': 'application/json'}
        try:
            with open('information.yaml', 'r') as ifh:
                self.doc = yaml.safe_load(ifh)

                # Getting general details
                self.time_interval = str(self.doc["general_details"]["chat_bot_read_time_interval"])

                # Getting JIRA server connection details
                self.jira_user = str(self.doc["jira_details"]["jira_user"])
                self.jira_password = str(self.doc["jira_details"]["jira_password"])
                self.jira_server_url = str(self.doc["jira_details"]["jira_server_url"])
                self.fixed_jira_query = str(self.doc["jira_details"]["fixed_jira_query"])
                self.string_header_with_response = str(self.doc["jira_details"]["string_header_with_response"])

                # Getting Webex Teams Room details
                self.webex_url = str(self.doc["webex_teams_details"]["webex_url"])
                self.webex_room_id = str(self.doc["webex_teams_details"]["webex_room_id"])

                # Getting Webex Teams Bot details
                self.auth_token = str(self.doc["webex_teams_details"]["auth_token"])
                self.webex_bot_name = str(self.doc["webex_teams_details"]["webex_bot_name"])

            # Setting Webex connectivity parameters
            self.webex_auth_headers['authorization'] = 'Bearer ' + self.auth_token

            # Creating connection to Jira server
            self.jira_object = self.jira_wrapper.get_jira_server_connection_object(jira_server_url = self.jira_server_url,
                                                                                   jira_user = self.jira_user,
                                                                                   jira_password = self.jira_password)
            self.logger.info("Periodic Bug Notifier, Initialization Complete!!!")
        except Exception as e:
            self.logger.info("Error -- {}".format(e))


    def start_script(self):
        """
            Starter method for periodic bug notifier utility
        """
        self.open_issues = self.jira_wrapper.run_jira_query(jira_object = self.jira_object,
                                                            jira_query = self.fixed_jira_query)
        self.data_to_send = self.jira_wrapper.formulate_message_to_send(room_id = self.webex_room_id,
                                                                        text_data = self.string_header_with_response,
                                                                        issues = self.open_issues,
                                                                        jira_server_url=self.jira_server_url,
                                                                        jira_object=self.jira_object)
        self.webex_wrapper.send_message_to_webex_group(webex_url = self.webex_url,
                                                       webex_auth_headers = self.webex_auth_headers,
                                                       data_to_send = self.data_to_send)


if __name__ == "__main__":
    bnu_obj = BugNotifierUtility()
    bnu_obj.start_script()
