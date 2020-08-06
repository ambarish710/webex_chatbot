import logging
from logging.handlers import RotatingFileHandler


class Logger:
    """
       Creates logger object for the Chat Bot Utility
    """
    def __init__(self):
        """
            Init Method, creating logger object
        """
        try:
            # Setting name and level for the logger object
            self.logger = logging.getLogger("chatbot_logger")
            self.logger.setLevel(logging.INFO)

            # Creating log file handler
            handler = RotatingFileHandler('chat_bot.log',
                                          maxBytes=5000000, backupCount=10)

            # Setting log level and creating logging format
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                          '%(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            # Adding handler to the logger object
            self.logger.addHandler(handler)

        except Exception as e:
            self.logger.error("Error creating logger object...\nError -- %s".format(e))
