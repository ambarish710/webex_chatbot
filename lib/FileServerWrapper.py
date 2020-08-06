import logging
import requests
import datetime


class FileServerWrapper:
    """
        File Server Wrapper Class which contains helper methods and other
        required generic variables
    """
    def __init__(self):
        """
            Init Method
            Declaring constants and creating logger object
        """
        self.logger = logging.getLogger('chatbot_logger')


    def get_build(self, url):
        """
            Returns latest build ID string from the given file server URL
            :param url: URL to access file server
            :return: Build ID string
        """
        try:
            latest = []
            last_upload_time = datetime.datetime.strptime("20-Feb-1991 00:00", '%d-%b-%Y %H:%M')
            response = requests.get(url)
            response_text = response.text
            if "404 Not Found" in response_text:
                _text = "Branch does not exist. Please provide correct branch prefix"
                self.logger.info(_text)
                return _text
            else:
                lines = response_text.split("\n")
                for line in lines:
                    if ".iso" in line:
                        el = line.split("         ")
                        el[:] = [item.strip() for item in el if item != '']
                        date_time_obj = datetime.datetime.strptime(el[1], '%d-%b-%Y %H:%M')
                        if date_time_obj > last_upload_time:
                            last_upload_time = date_time_obj
                            latest = el
                build = str(latest[0]).split('"')[1]
                self.logger.info("Build: {}".format(build))
                return build
        except Exception as e:
            self.logger.error("Failed to connect to fileserver...")
            self.logger.error("Error: {}".format(e))
