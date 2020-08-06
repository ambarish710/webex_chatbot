***************--------------------------------------------------------------------------------***************
                                              ChatBot Utility
***************--------------------------------------------------------------------------------***************


        The idea behind creating this utility was to provide an interactive information assistance tool which can be used for various practical purposes like getting build report, getting last promoted build for a branch, troubleshooting a cluster, tracking incoming bugs for a release, information acquisition, automate other repetitive tasks etc.
 

General Information --
    This utility provides the following features --
        1. Periodic Notifier Feature --
            - Runs the given fixed jira query provided in information.yaml (jira_details:fixed_jira_query)
            - Collects the list of bugs associated with the Jira query
            - Sends the formatted list of bugs to the given Webex Teams Group provided in information.yaml after/at
              the specified time interval

        2. ChatBot Feature --
            - Monitors the given Webex Teams Group [provided in information.yaml (webex_teams_details:webex_room_id)]
            - Reads the user input, checks if its a valid keyword and responds accordingly,
                - If the user input is "Adding New Keyword",
                    - Adds a new keyword along with the respective query to the keyword_query_mappings.yaml
                    - @BUG_NOTIFIER_BOT Add Keyword > <KEYWORD> : <JIRA QUERY>
                - If the user input is "Deleting Existing Keyword",
                    - Deletes existing keyword from the keyword_query_mappings.yaml
                    - @BUG_NOTIFIER_BOT Delete Keyword > <KEYWORD> : <JIRA QUERY>
                - If there is a JIRA query associated with the keyword,
                    - Collects the list of bugs associated with the JIRA query
                    - Sends the formatted list of bugs to the Webex Teams Group along with the bug count
                    - @BUG_NOTIFIER_BOT <KEYWORD>
                - If the user input is "help" keyword,
                    - Collects the list of all the keywords present
                    - Sends the formatted list of all the keywords to the Webex Teams Group
                    - @BUG_NOTIFIER_BOT help
                - If the user input is "Get Testing Status" for a given build,
                    - Collects the overall testing status of the build from QDNA server
                    - Sends the regression status report to the  Webex Teams Group
                    - @BUG_NOTIFIER_BOT Get Testing Status: <COMPONENT> <BUILD-ID>
                - If the user input is "Get Detailed Testing Status" for a given build,
                    - Collects the detailed testing status from QDNA server for all the jobs ran against the build
                    - Sends the detailed regression status report to the  Webex Teams Group
                    - @BUG_NOTIFIER_BOT Get Detailed Testing Status: <COMPONENT> <BUILD-ID>
                - If the user input is "Get Bug Details" for a given bug,
                    - Collects bug details from JIRA server
                    - Sends the bug detail report to the  Webex Teams Group
                    - @BUG_NOTIFIER_BOT Get Bug Details: <BUG-ID>
                - If the user input is "Get last promoted build" for a given branch
                    - Collects last promoted build for that given branch from fileserver
                    - Sends build ID to the  Webex Teams Group
                    - @BUG_NOTIFIER_BOT Get last promoted build <BRANCH>
                - If the user input is "Get current build" for a given branch
                    - Collects the build ID for which regressions are running
                    - Sends build ID to the  Webex Teams Group
                    - @BUG_NOTIFIER_BOT Get current build <BRANCH>
                - If the user input is "Troubleshoot" a given cluster
                    - Then it runs a set of troubleshooting commands on a given cluster
                    - And provides report in personal chat
                    - @BUG_NOTIFIER_BOT Troubleshoot <HOSTNAME> <SSH_USERNAME> <SSH_PASSWORD> <CLUSTER_USERNAME> <CLUSTER_PASSWORD>
            - Stores the last served request timestamp in "tmp/metadata.yaml" (Readonly)



Usage --
    - To track incoming/existing bugs for a given release periodically
    - To check build regression status
    - Troubleshoot a cluster
    - To get current/last promoted build for a branch
    - etc.



Setup and Installation --
    1. Create a virtual environment and run the following command (preferably with python 2.7), to install all the
       dependency packages required by "Webex Teams Notifier Utility"
            --  "pip install -r requirements.txt"


    2. Update information.yaml with details about Jira Server, CDET Server, Webex Teams Group, & QDNA server details --
            general_details:
                chat_bot_read_time_interval: 5                              # Time interval in between 2 consecutive read checks
                periodic_notifier_interval: 6                               # Future Paramter for scheduling periodic bug notifier (Cronjob input)
                proxy: true/false
                http_proxy: "PROXY"
                https_proxy: "PROXY"

            jira_details:
                jira_user: "JIRA_USERNAME"                                  #base64encoded
                jira_password: "JIRA_PASSWORD"
                jira_server_url: "JIRA_SERVER_URL"                          # Jira Backend URL [Hardcoded]
                fixed_jira_query: "FIXED_JIRA_QUERY"                        # Fixed Jira query used by periodic bug notifier
                string_header_with_response: "Here are the Bugs --\n"       # Example

            cdet_details:
                cdet_user: "CDET_USER"
                cdet_password: "CDET_PASSWORD"
                auth_token: "TOKEN"
                cdet_url: "CDET_BACKEND_URL"
                fixed_cdet_query: "CDET_QUERY"
                string_header_with_response: "TEXT"

            webex_teams_details:
                webex_url: "WEBEX_BASE_URL"                                 # Webex Teams Backend URL [Hardcoded]
                webex_room_id: "WEBEX_ROOM_ID"
                # Webex Bot details
                auth_token: "TOKEN"                                         # Can be found here https://developer.webex.com/my-apps/bug_notifier_bot
                webex_bot_name: "BOT_NAME"

            qdna_details:
                cluster_ip: "IP"
                username: "username"
                password: "password"



Running the Utility --
    - You can run the utility using the following command --
        - "nohup sh run.sh &"


Logging information --
    - Tool logs can be found in "chat_bot.log"
    - Log Rotation Policy --
        - Logs will be rotated automatically when log file size goes above 5 MB
        - Last 10 log files will be preserved (last 50 MB logs)



Current pending Development Tasks --
    - Creating an install script to install the tool



Future Enhancements --
    - Converting the utility into an NLP AI driven tool wherein it understands user input given in human readable
      format converts it to a valid Jira query (NLP Advancement)
    - Monitoring bugs tagged for a release as they go in “Dev-Complete” state and assign them to respective
      QA folks and sending notification to them in person
    - Changing fields of bug or list of bugs from the chatbot
    - Currently, the bot monitors the group after every 10 seconds (tunable parameter) and serves the last request. Improving response time by using kafka as a message broker instead to serve this purpose, so that messages are not lost and served efficiently
    - Notifying “QA TEST GROUPS” with build or regression job failures
    - Currently the bot uses a hardcoded set of commands as part of troubleshooting a cluster. Add an enhancement to allow users to provide his own troubleshoot command set yaml.
    - Trigger builds from the bot
    - Jenkins Integration
    - Run a specific command against a cluster
    - Update JIRA bug



Important Links --
    - https://developer.webex.com/docs/platform-introduction
    - https://developer.webex.com/docs/bots
    - https://jira.readthedocs.io/en/master/
    - https://jira.readthedocs.io/en/master/api.html
    - https://qdna.cisco.com/
    - https://confluence-eng-sjc1.cisco.com/conf/pages/viewpage.action?spaceKey=QDNA&title=QDNA+Dashboard+Service
