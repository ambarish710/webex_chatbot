import base64
import logging
from jira import JIRA



class JiraConnectionWrapper:
    """
        Jira Connection Wrapper Class that contains helper methods
    """
    def __init__(self):
        """
            Init Method

        """
        self.logger = logging.getLogger('chatbot_logger')


    def get_jira_server_connection_object(self, jira_server_url, jira_user, jira_password):
        """
            Creates connection to JIRA server
            :return: JIRA server connection object
        """
        try:
            self.logger.info("Connecting to JIRA server: {}".format(jira_server_url))
            jira_options = {'server': jira_server_url}
            # Connecting to Jira server
            jira = JIRA(options=jira_options,
                        basic_auth=(base64.b64decode(jira_user),
                                    base64.b64decode(jira_password)))
            self.logger.info("Successfully connected to JIRA server!!!")
            return jira
        except Exception as e:
            self.logger.error("Failed to connect to JIRA server: {}".format(e))


    def run_jira_query(self, jira_object, jira_query):
        """
            Runs a given jira query on the JIRA server
            and return list of issues
            :param jira_object: JIRA connection object
            :param jira_query: Valid jira query to run
            :return: List of issues
        """
        try:
            self.logger.info("Running the following JIRA query on JIRA server...")
            self.logger.info("Jira Query: {}".format(jira_query))
            open_issues = jira_object.search_issues(jira_query, startAt=0,
                                                    maxResults=0, json_result=False)
            self.logger.info("Response: {}".format(open_issues))
            return open_issues
        except Exception as e:
            self.logger.error("Failed to get a response for the JIRA query: {}".format(e))


    def formulate_message_to_send(self, room_id, text_data, issues, jira_server_url, jira_object):
        """
            Lists open issues and populates required variables
            :param issues: List of open issues
            :param room_id: Webex room ID
            :param text_data: Data
            :return: Data to send variable
        """
        data_to_send = {}
        bug_count = 0
        data_to_send["roomId"] = room_id
        four_spaces = "&nbsp;&nbsp;&nbsp;&nbsp;"
        seven_spaces = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        if (issues):
            text_data += "<br />"
            for issue in issues:
                issue_str = str(issue)
                self.logger.info("Issue: {}".format(issue_str))
                link = "{}browse/{}".format(jira_server_url,issue_str)
                self.logger.info("Link: {}".format(link))
                bug_details = jira_object.issue(issue_str)
                text_data += "[{}]({}),{}Assignee: {},{}Summary: {}<br />".format(issue_str, link,
                                                                                  four_spaces,
                                                                                  bug_details.fields.assignee,
                                                                                  seven_spaces,
                                                                                  bug_details.fields.summary[:75])
                bug_count += 1
        else:
            self.logger.info("No Issues found with the given jira query")
        text_data += "Total Bugs: {}".format(bug_count)
        self.logger.info("Data to send: {}".format(text_data))
        data_to_send["markdown"] = text_data
        return data_to_send


    def get_bug_details(self, jira_object, bug_id):
        """
            Using the given bug ID return text string that contains
            Bug Heading, Bug Priority, Bug Assignee, Bug Reporter,
            Bug Created, Bug Status, Bug Labels
            :param bug_id: Bug ID
            :param jira_object: JIRA object
            :return: Text string with above mentioned details
        """
        details = "Here are the bug details --\n"
        issue = jira_object.issue(bug_id)
        # Bug Heading
        details += "\t" + "Bug Heading: {}\n".format(issue.fields.summary)
        self.logger.info("Bug Heading: {}".format(issue.fields.summary))
        # Bug Priority
        details += "\t" + "Priority: {}\n".format(issue.fields.priority)
        self.logger.info("Priority: {}".format(issue.fields.priority))
        # Bug Assignee
        details += "\t" + "Assignee: {}\n".format(issue.fields.assignee)
        self.logger.info("Assignee: {}".format(issue.fields.assignee))
        # Bug Reporter
        details += "\t" + "Reporter: {}\n".format(issue.fields.reporter)
        self.logger.info("Reporter: {}".format(issue.fields.reporter))
        # Bug Created
        details += "\t" + "Created: {}\n".format(issue.fields.created)
        self.logger.info("Created: {}".format(issue.fields.created))
        # Bug Status
        details += "\t" + "Status: {}\n".format(issue.fields.status)
        self.logger.info("Status: {}".format(issue.fields.status))
        # Bug Labels
        details += "\t" + "Labels: {}\n".format(issue.fields.labels)
        self.logger.info("Labels: {}".format(issue.fields.labels))
        return details


    def get_bugs_filed_for_build(self, ):
        """

            :return:
        """