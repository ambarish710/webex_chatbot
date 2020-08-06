from crontab import CronTab



class Installer:
    def __init__(self):
        """
            Init Method
        """


    def setup_cronjob_for_periodic_bug_notifier(self):
        """
            Sets up cronjob for periodic bug notifier
        """
        # init cron
        cron = CronTab()
        # add new cron job
        job = cron.new(command='python periodic_bug_notifier.py')
        # job settings
        job.hour.every(self.periodic_notifier_interval)


    def install_script(self):
        """
            Runs the install script
        """
        self.get_jira_input()


    def startscript(self):
        """
            Starts the installation process
        """




if __name__ == "__main__":
    installer_obj = Installer()
    installer_obj.startscript()
