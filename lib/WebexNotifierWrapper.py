import logging
from GenericWrappper import GenericWrappper



class WebexNotifierWrapper:
    """
        Webex Notifier Wrapper Class that contains helper methods
    """
    def __init__(self):
        self.logger = logging.getLogger('chatbot_logger')
        self.generic_wrapper = GenericWrappper()


    def send_message_to_webex_group(self, webex_url, webex_auth_headers, data_to_send):
        """
            Send message to given webex teams group
            :param webex_url: Webex Teams Backend URL
            :param webex_auth_headers: Webex Teams Authentication header
            :param data_to_send: Data
            :return: Output from the POST API call
        """
        self.logger.info("Webex Teams authentication header: {}".format(webex_auth_headers))
        self.logger.info("Webex URL: {}".format(webex_url))
        self.logger.info("Data to send: {}".format(data_to_send))
        try:
            # Send message to webex group
            output = self.generic_wrapper.requests_post(url = webex_url, data=data_to_send,
                                                        headers = webex_auth_headers)
            self.logger.info("Response: {}".format(output))
            return output
        except Exception as e:
            self.logger.error("Error: {}".format(e))


    def receive_message_from_webex_group(self, webex_url, webex_auth_headers):
        """
            Receive message from a given webex teams group
            :param webex_url: Webex Teams Backend URL
            :param webex_auth_headers: Webex Teams Authentication header
            :return: Output from the GET API call
        """
        self.logger.info("Webex Teams authentication header: {}".format(webex_auth_headers))
        self.logger.info("Webex URL: {}".format(webex_url))
        try:
            # Receiving message from a webex group
            output = self.generic_wrapper.requests_get(url = webex_url,
                                                       headers = webex_auth_headers)
            #self.logger.info("Response: {}".format(output))
            return output
        except Exception as e:
            self.logger.error("Error: {}".format(e))
