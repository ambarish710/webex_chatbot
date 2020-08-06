import json
import re
import yaml
from ruamel.yaml import YAML
import dateutil.parser
import logging
import sys
import multiprocessing

from lib.Logger import Logger
from lib.GenericWrappper import GenericWrappper
from lib.JiraConnectionWrapper import JiraConnectionWrapper
from lib.WebexNotifierWrapper import WebexNotifierWrapper
from lib.QdnaConnectorWrapper import QdnaConnectorWrapper
from lib.SshWrapper import SshWrappper
from lib.FileServerWrapper import FileServerWrapper



class ChatBotUtility:
    def __init__(self):
        """
            Initializes and sets required default global variables by
            collecting metadata from information.yaml
        """
        self.ru_yaml = YAML()
        self.ru_yaml.width = 4096
        self.logger_object = Logger()
        self.webex_wrapper = WebexNotifierWrapper()
        self.logger = logging.getLogger('chatbot_logger')
        self.logger.info("Starting default initialization...")
        self.webex_auth_headers = {'content-type': 'application/json'}
        try:
            # Collecting metadata from information.yaml
            with open('information.yaml', 'r') as ifh:
                self.doc = yaml.safe_load(ifh)

                # Getting Webex Teams Room details
                self.webex_url = str(self.doc["webex_teams_details"]["webex_url"])
                self.webex_room_id = str(self.doc["webex_teams_details"]["webex_room_id"])

                # Getting Webex Teams Bot details
                self.auth_token = str(self.doc["webex_teams_details"]["auth_token"])
                self.webex_bot_name = str(self.doc["webex_teams_details"]["webex_bot_name"])

            # Setting Webex connectivity parameters
            self.webex_auth_headers['authorization'] = 'Bearer ' + self.auth_token
            self.webex_auth_headers['Accept'] = 'application/json'
            # Removing '+ "&max=1"' for now from webex_teams_get_url bcoz of
            # the webex list messages API issue -- including max parameter
            # impacts the sort order of the message results when bot calls
            # list messages api
            self.webex_teams_get_url = self.webex_url + "?mentionedPeople=me" \
                                       + "&roomId=" + self.webex_room_id

            self.logger.info("Default initialization complete!!!")
        except Exception as e:
            self.logger.error("Error -- {}".format(e))


    def intialize_prerequisites(self):
        """
            Initializes and sets other default prerequisites for the
            utility by collecting metadata from information.yaml
        """
        self.logger.info("Initializing pre-requisites...")
        self.generic_wrapper = GenericWrappper()
        self.EDIT_KEYWORDS = ['add', 'delete']
        try:
            # Collecting info from keyword_query_mappings.yaml
            with open('keyword_query_mappings.yaml', 'r') as kfh:
                self.mappings = self.ru_yaml.load(kfh)

                # Getting jira keyword query mappings
                self.keyword_jira_query_mappings = self.mappings["keyword_jira_query_mappings"]
                self.logger.info("Keyword Query mappings -- {}".format(self.keyword_jira_query_mappings))

            self.logger.info("Pre-Requisite initialization complete!!!")
        except Exception as e:
            self.logger.error("Error -- {}".format(e))


    def intialize_jira_prerequisites(self):
        """
            Initializes and sets required prerequisites for jira queries
            by collecting metadata from information.yaml
        """
        self.logger.info("Initializing pre-requisites for JIRA...")
        self.jira_wrapper = JiraConnectionWrapper()
        try:
            # Collecting info from information.yaml
            with open('information.yaml', 'r') as ifh:
                self.doc = yaml.safe_load(ifh)

                # Getting JIRA server connection details
                self.jira_user = str(self.doc["jira_details"]["jira_user"])
                self.jira_password = str(self.doc["jira_details"]["jira_password"])
                self.jira_server_url = str(self.doc["jira_details"]["jira_server_url"])
                self.fixed_jira_query = str(self.doc["jira_details"]["fixed_jira_query"])

            # Creating connection to Jira server
            self.jira_object = self.jira_wrapper.get_jira_server_connection_object(jira_server_url=self.jira_server_url,
                                                                                   jira_user=self.jira_user,
                                                                                   jira_password=self.jira_password)

            self.logger.info("Pre-Requisite initialization for JIRA complete!!!")
        except Exception as e:
            self.logger.error("Error -- {}".format(e))


    def intialize_qdna_prerequisites(self):
        """
            Initializes and sets other required prerequisites for qdna
            queries by collecting metadata from information.yaml
        """
        self.logger.info("Initializing pre-requisites for QDNA...")
        try:
            # Collecting info from information.yaml
            with open('information.yaml', 'r') as ifh:
                self.doc = yaml.safe_load(ifh)

                # Getting QDNA details
                self.qdna_cluster_ip = str(self.doc["qdna_details"]["cluster_ip"])
                self.qdna_username = str(self.doc["qdna_details"]["username"])
                self.qdna_password = str(self.doc["qdna_details"]["password"])

            # Creating QDNA connection object
            self.qdna_wrapper = QdnaConnectorWrapper(self.qdna_cluster_ip, self.qdna_username, self.qdna_password)

            self.logger.info("Pre-Requisite initialization for QDNA complete!!!")
        except Exception as e:
            self.logger.error("Error -- {}".format(e))


    def intialize_tshoot_prerequisites(self):
        """
            Initializes and sets other required prerequisites for
            troubleshoot queries by collecting metadata from
            commands.yaml
        """
        self.logger.info("Initializing pre-requisites for troubleshooting...")
        try:
            self.ssh_wrapper = SshWrappper()
            self.all_commands = {}
            with open('commands.yaml', 'r') as ifh:
                self.all_commands = yaml.safe_load(ifh)
            self.logger.info("Pre-Requisite initialization for troubleshooting complete!!!")
        except Exception as e:
            self.logger.error("Error -- {}".format(e))


    def intialize_fileserver_prerequisites(self, branch):
        """
            Initializes and sets other required prerequisites to access
            maglev fileserver
            :param branch: Branch ID
        """
        self.logger.info("Initializing pre-requisites for fileserver...")
        self.fileserver_wrapper = FileServerWrapper()
        self.logger.info("Branch: {}".format(branch))
        _file_server_url = 'http://maglev-fileserver.cisco.com/artifacts/daily-release/iso-release/'
        self.get_stable_build_url = _file_server_url + 'stable/{}/'.format(branch)
        self.get_current_build_url = _file_server_url + 'daily/{}/'.format(branch)


    def formulate_and_send_message_to_webex_group(self, text_data, metadata, message_time):
        """
            Formulate message and then send it to the webex group
            :param text_data: text to send
            :param metadata: metadata to update
            :param message_time: message time
        """
        data_to_send = {}
        data_to_send["roomId"] = self.webex_room_id
        data_to_send["text"] = text_data
        self.webex_wrapper.send_message_to_webex_group(webex_url=self.webex_url,
                                                       webex_auth_headers=self.webex_auth_headers,
                                                       data_to_send=data_to_send)
        self.generic_wrapper.update_timestamp(metadata, message_time)
        self.logger.info("---***--- Reply sent to the Webex group ---***---")


    def formulate_and_send_message_to_individual(self, text_data, person_id):
        """
            Formulate message and then send it to the given individual
            :param text_data: text to send
            :param metadata: metadata to update
            :param message_time: message time
            :param person_id: Webex person ID
        """
        data_to_send = {}
        data_to_send["toPersonId"] = person_id
        data_to_send["markdown"] = text_data
        self.webex_wrapper.send_message_to_webex_group(webex_url=self.webex_url,
                                                       webex_auth_headers=self.webex_auth_headers,
                                                       data_to_send=data_to_send)
        self.logger.info("---***--- Reply sent to the individual ---***---")


    def get_testing_status(self, last_message):
        """
            Get generic testing status for a given build in a project and
            return text ouput
            :param last_message: last message
            :return: build statistics in string format
        """
        entity = re.split('[: ]', last_message)
        self.logger.info("Last message tokens: {}".format(entity))
        project = entity[4]
        build_id = entity[5]
        self.logger.info("Project: {}".format(project))
        self.logger.info("Build ID: {}".format(build_id))
        return_text = self.qdna_wrapper.get_testing_status_from_qdna(project=project, build_id=build_id)
        return return_text


    def get_detailed_testing_status(self, last_message):
        """
            Get detailed testing status for a given build in a project and
            return text ouput
            :param last_message: last message
            :return: build statistics in string format
        """
        entity = re.split('[: ]', last_message)
        self.logger.info("Last message tokens: {}".format(entity))
        project = entity[5]
        build_id = entity[6]
        self.logger.info("Project: {}".format(project))
        self.logger.info("Build ID: {}".format(build_id))
        return_text = self.qdna_wrapper.get_detailed_testing_status_from_qdna(project=project,
                                                                              build_id=build_id)
        return return_text


    def edit_keyword_jira_query_mappings(self, last_message, metadata, message_time):
        """
            Edit keyword_query_mappings.yaml depending upon user input.
            Add a new keyword or delete existing keyword
            :param last_message: Last message recieved
            :param metadata: metadata to update
            :param message_time: message time
        """
        entity = re.split('[>:]', last_message)
        self.logger.info("Last message tokens: {}".format(entity))
        try:
            with open('keyword_query_mappings.yaml', 'w') as kfh:
                # Check if incoming message has "add keyword" in it
                if "add keyword" in entity[0].lower() and len(entity) == 3:
                    self.logger.info("Adding keyword to the existing list --")
                    self.logger.info("{} : {}".format(entity[1].strip(), entity[2].strip()))
                    self.mappings["keyword_jira_query_mappings"][entity[1].strip()] = entity[2].strip()
                    self.ru_yaml.dump(self.mappings, kfh)
                    text = "Successfully added given keyword to the existing list!!!"
                    self.logger.info(text)
                    self.formulate_and_send_message_to_webex_group(text, metadata, message_time)

                # Check if incoming message has "delete keyword" in it
                elif "delete keyword" in entity[0].lower() and len(entity) == 3:
                    self.logger.info("Deleting keyword from the existing list if present --")
                    self.logger.info("{} : {}".format(entity[1].strip(), entity[2].strip()))
                    if entity[1].strip() in self.keyword_jira_query_mappings:
                        del self.mappings["keyword_jira_query_mappings"][entity[1].strip()]
                        self.ru_yaml.dump(self.mappings, kfh)
                        text = "Successfully deleted given keyword from the existing list!!!"
                        self.logger.info(text)
                        self.formulate_and_send_message_to_webex_group(text, metadata, message_time)
                    else:
                        self.ru_yaml.dump(self.mappings, kfh)
                        text = "Keyword does not exist..."
                        self.logger.info(text)
                        self.formulate_and_send_message_to_webex_group(text, metadata, message_time)

                else:
                    self.ru_yaml.dump(self.mappings, kfh)
                    text = "Un-indentified keyword..."
                    self.logger.info(text)
                    self.formulate_and_send_message_to_webex_group(text, metadata, message_time)

        except Exception as e:
            text = "Failure in updating keyword_query_mappings.yaml file,\nError: {}".format(e)
            self.logger.error(text)
            self.formulate_and_send_message_to_webex_group(text, metadata, message_time)


    def formulating_command_output(self, output, error, person_id, text):
        """
            Sending message to individual
            :param output: stdout of the executed command
            :param error: stderr of the executed command
            :param person_id: Webex person ID
            :param text: text to send
        """
        decoded_output = output.read().decode('utf8')
        decoded_error = error.read().decode('utf8')
        # Sending command output
        if decoded_output:
            self.logger.info("Output: {}".format(decoded_output))
            text += "```\n" + decoded_output + "\n```"
        if decoded_error:
            self.logger.info("Error: {}".format(decoded_error))
            text += "```\n" + decoded_error + "\n```"
        self.formulate_and_send_message_to_individual(text, person_id)


    def execute_commands_on_cluster(self ,hostname, ssh_username, ssh_password,
                                    maglev_username, maglev_password, person_id):
        """
            Execute commands on the cluster
            :param hostname: Hostname
            :param ssh_username: SSH Username
            :param ssh_password: SSH Password
            :param maglev_username: maglev username
            :param maglev_password: maglev password
            :param person_id: Webex person ID
        """
        # Connecting to the given cluster
        self.ssh, self.pingstatus = self.ssh_wrapper.connect(hostname=hostname,
                                            username=ssh_username,
                                            password=ssh_password)
        if self.pingstatus == 0:
            text = "Hello!!!<br />This is MaQ<br />"
            text += "I just got a request to troubleshoot this cluster -- {}<br />".format(hostname)
            text += "Here is the report --<br />"
            for command_set in self.all_commands:
                self.logger.info("Command Set: {}".format(command_set))
                if self.all_commands[command_set]:
                    if command_set == "maglev_commands":
                        text += "command: {}\n".format(command)
                        command = "maglev login -u {} -p {} -c {}:443 -k".format(maglev_username, maglev_password, hostname)
                        stdin, stdout, stderr = self.ssh.exec_command(command, timeout=20)
                        # Sending command output to the individual
                        self.formulating_command_output(stdout, stderr, person_id, text)
                        text = ""
                    for command in self.all_commands[command_set]:
                        text += "command: {}\n".format(command)
                        self.logger.info("Executing " + str(text))
                        stdin, stdout, stderr = self.ssh.exec_command(command, timeout=20)
                        # Sending command output to the individual
                        self.formulating_command_output(stdout, stderr, person_id, text)
                        text = ""
            # Sending tshoot completed reply
            text = "Troubleshooting Completed!!!<br />"
            self.logger.info(text)
            self.formulate_and_send_message_to_individual(text, person_id)
            # Closing SSH connection
            self.ssh.close()
            self.logger.info('SSH Connection Closed!!!')
        else:
            text = "Cluster is not reachable..."
            self.logger.info(text)
            self.formulate_and_send_message_to_individual(text, person_id)


    def tshoot_cluster(self, last_message, metadata, message_time, person_id):
        """
            Troubleshoot given cluster
            :param last_message: last message
            :param metadata: metadata to update
            :param message_time: message time
            :param person_id: Webex person ID
        """
        entity = re.split(' ', last_message)
        self.generic_wrapper.update_timestamp(metadata, message_time)
        if len(entity) == 6:
            hostname = entity[1]
            ssh_username = entity[2]
            ssh_password = entity[3]
            maglev_username = entity[4]
            maglev_password = entity[5]
            self.logger.info("IP: {}".format(hostname))
            self.logger.info("SSH username: {}".format(ssh_username))
            self.logger.info("SSH password: {}".format(ssh_password))
            self.logger.info("maglev username: {}".format(maglev_username))
            self.logger.info("maglev password: {}".format(maglev_password))
            self.intialize_tshoot_prerequisites()
            tshoot_process = multiprocessing.Process(target=self.execute_commands_on_cluster,
                                         args=(hostname, ssh_username,
                                               ssh_password, maglev_username,
                                               maglev_password, person_id))
            tshoot_process.start()
            tshoot_process.join()
        else:
            self.unidentified_keyword(metadata, message_time)


    def unidentified_keyword(self, metadata, message_time):
        """

            :param metadata: metadata to update
            :param message_time: message time
        """
        text = "Sorry, I didn't quite understand what you're trying to say..."
        self.logger.error(text)
        self.formulate_and_send_message_to_webex_group(text, metadata, message_time)


    def reply_to_message(self, current_message_datetime, last_served_request,
                         last_message, metadata, message_time, person_id):
        """
            Read the message and reply accordingly
            :param current_message_datetime: current message time in datetime format
            :param last_served_request: last served request time
            :param last_message: last message content
            :param metadata: metadata to update
            :param message_time: message time
        """
        # Read message and reply accordingly
        if current_message_datetime > last_served_request:
            self.logger.info("Received new message/keyword...")
            self.intialize_prerequisites()

            # Test keyword
            if last_message == "Valar Morghulis":
                self.logger.info("Test keyword identified..., sending reply!!!")
                self.formulate_and_send_message_to_webex_group(self.keyword_jira_query_mappings[last_message],
                                                               metadata, message_time)

            # Help keyword
            elif last_message.lower() == "help":
                self.logger.info("Keyword identified..., user needs help!!!")
                text = self.generic_wrapper.HELP_TEXT
                text += "\nKeyword to jira query mappings available:\n"
                for key, value in self.keyword_jira_query_mappings.iteritems():
                    text += "\t" + str(key) + "\t-->\t" + str(value) + "\n"
                self.formulate_and_send_message_to_webex_group(text, metadata, message_time)

            # Editing keyword_query_mappings.yaml file
            elif any(word in re.split('[>:]', last_message.lower())[0].strip() for word in self.EDIT_KEYWORDS):
                self.logger.info("Keyword identified...")
                self.logger.info("User wants to edit keyword_query_mappings.yaml")
                self.edit_keyword_jira_query_mappings(last_message,
                                                      metadata, message_time)

            # Provide bug description
            elif "get bug details" in last_message.lower():
                self.logger.info("Keyword identified...")
                self.logger.info("User wants details about a bug")
                self.intialize_jira_prerequisites()
                bug_id = last_message.split(" ")[3]
                self.logger.info("Bug ID: {}".format(bug_id))
                details = self.jira_wrapper.get_bug_details(jira_object=self.jira_object,
                                                          bug_id=bug_id)
                self.formulate_and_send_message_to_webex_group(details, metadata, message_time)

            # Provide last promoted build ID for a given branch
            elif "get last promoted build" in last_message.lower():
                self.logger.info("Keyword identified...")
                self.logger.info("User wants to know the last promoted build from a branch")
                branch = last_message.split(" ")[4]
                self.logger.info("Branch: {}".format(branch))
                self.intialize_fileserver_prerequisites(branch)
                details = self.fileserver_wrapper.get_build(url=self.get_stable_build_url)
                self.formulate_and_send_message_to_webex_group(details, metadata, message_time)

            # Provide current build ID for a given branch
            elif "get current build" in last_message.lower():
                self.logger.info("Keyword identified...")
                self.logger.info("User wants to know the current build from a branch")
                branch = last_message.split(" ")[3]
                self.logger.info("Branch: {}".format(branch))
                self.intialize_fileserver_prerequisites(branch)
                details = self.fileserver_wrapper.get_build(url=self.get_current_build_url)
                self.formulate_and_send_message_to_webex_group(details, metadata, message_time)

            # Get testing status for a given build
            elif "get testing status" in last_message.lower():
                self.logger.info("Keyword identified...")
                self.logger.info("User wants testing info about a build")
                self.intialize_qdna_prerequisites()
                return_text = self.get_testing_status(last_message)
                self.formulate_and_send_message_to_webex_group(return_text, metadata, message_time)

            # Get detailed testing status for a given build
            elif "get detailed testing status" in last_message.lower():
                self.logger.info("Keyword identified...")
                self.logger.info("User wants detailed testing info about a build")
                self.intialize_qdna_prerequisites()
                return_text = self.get_detailed_testing_status(last_message)
                self.formulate_and_send_message_to_webex_group(return_text, metadata, message_time)

            # Troubleshoot a given cluster
            elif "troubleshoot" in last_message.lower():
                self.logger.info("Keyword identified...")
                self.logger.info("User wants to troubleshoot/debug given cluster")
                self.tshoot_cluster(last_message, metadata, message_time, person_id)

            # Get bugs raised on a given build
            elif "get bugs for build" in last_message.lower():
                self.logger.info("Keyword identified...")
                self.logger.info("User wants to get the list of bugs filed for a build")
                return_text = self.jira_wrapper.get_bugs_filed_for_build()
                self.formulate_and_send_message_to_webex_group(return_text, metadata, message_time)

            # Executing jira query associated with the keyword
            elif last_message in self.keyword_jira_query_mappings:
                reply_text = "Here are " + last_message + " --\n"
                self.logger.info("Keyword identified..., sending reply now")
                self.intialize_jira_prerequisites()
                jira_query_to_run = self.keyword_jira_query_mappings[last_message]
                open_issues = self.jira_wrapper.run_jira_query(jira_object=self.jira_object,
                                                             jira_query=jira_query_to_run)
                data_to_send = self.jira_wrapper.formulate_message_to_send(room_id=self.webex_room_id,
                                                                           text_data=reply_text,
                                                                           issues=open_issues,
                                                                           jira_server_url=self.jira_server_url,
                                                                           jira_object=self.jira_object)
                self.webex_wrapper.send_message_to_webex_group(webex_url=self.webex_url,
                                                            webex_auth_headers=self.webex_auth_headers,
                                                            data_to_send=data_to_send)
                self.generic_wrapper.update_timestamp(metadata, message_time)
                self.logger.info("---***--- Reply sent to the Webex group ---***---")

            # Keyword not identified
            else:
                self.unidentified_keyword(metadata, message_time)
                self.generic_wrapper.update_timestamp(metadata, message_time)
        else:
            self.logger.info("This message was already served at: {}".format(last_served_request))
            self.logger.info("---***--- Nothing to serve in this iteration!!! ---***---")


    def monitor_webex_group_and_take_action(self):
        """
            As the name suggests this method monitors the given webex
            group. Whenever it receives a message where
            "BUG_NOTIFIER_BOT" is specified and there is a specific
            entry in keyword_jira_query_mappings in information.yaml
            then it executes the given query on Jira server and returns
            respective response
        """
        try:
            self.logger.info("---***--- Iteration Start!!! ---***---")

            # Collecting info from metadata.yaml
            with open('tmp/metadata.yaml', 'r') as mfh:
                metadata = yaml.safe_load(mfh)
                last_served_request = dateutil.parser.parse(metadata["read_only"]["last_served_request"])
            self.logger.info("Last served request time: {}".format(last_served_request))

            # Getting the last message in the group where bot was mentioned
            output = self.webex_wrapper.receive_message_from_webex_group(webex_url=self.webex_teams_get_url,
                                                                         webex_auth_headers=self.webex_auth_headers)
            self.logger.info("Ouput response -- {}".format(output))
            self.logger.info("Output content -- {}".format(output.content))
            json_output = json.loads(output.content)
            last_message = json_output["items"][0]["text"].replace(self.webex_bot_name + " ","")
            person_id = json_output["items"][0]["personId"]
            current_message_datetime = dateutil.parser.parse(json_output["items"][0]["created"])
            message_time = str(json_output["items"][0]["created"])
            self.logger.info("Current message -- {}".format(last_message))
            self.logger.info("Current message time: {}".format(message_time))

            # Sending reply
            self.reply_to_message(current_message_datetime, last_served_request,
                                  last_message, metadata, message_time, person_id)

            self.logger.info("---***--- Iteration End!!! ---***---")
        except Exception as e:
            self.logger.error("Error: {}".format(e))
            sys.exit()


    def starter(self):
        """
            Starter method for the chat bot utility
        """
        self.monitor_webex_group_and_take_action()



if __name__ == "__main__":
    cbu_obj = ChatBotUtility()
    cbu_obj.starter()
