########################
## RUNTIME VARIABLES ##
########################
ENVIRONMENT = "dev"  # "dev" or "prod"

####################################
## BOT CONFIGURATION VARIABLES ##
####################################
BOT_PREFIX = "?"
DEFAULT_ACTIVITY_TEXT = "Datascience tutorials"
OWNER_ID = 730762300503490650
PRIMARY_GUILD_ID = 762774569827565569


####################################
## SERVER CONFIGURATION VARIABLES ##
####################################
AUTOMATE_CHANNEL = 1078142748747644988
AUTOMATE_WEBHOOK_ID = 1078142811725123594
DEV_LOGS_CHANNEL = 1109115993701232670

ADMIN_ID = 730762300503490650
QUALIFIER_ROLE = 780935056540827729
DOT_ONE_ROLE = 1078208692853420073
DOT_TWO_ROLE = 1078208892296761404
DOT_THREE_ROLE = 1078208973326536724
SPAM_ROLE = 1078208518793994240

LIVE_SESSION_PING_ROLE = None if ENVIRONMENT == "prod" else 1131210834744447067
LIVE_SESSION_CALENDARS = [
    {
        "name": "English 1 - May 23",
        "id": "c_rviuu7v55mu79mq0im1smptg3o%40group.calendar.google.com",
        "key": "AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs",
        "channel": 780959983301820426 if ENVIRONMENT == "prod" else 1104485755637735458,
    },
    {
        "name": "Maths 1 - May 23",
        "id": "c_a9c3c9118e64ae5e1746d451d79ee9775cd2e7c6c9237f3c0bc8cd4504d37ded%40group.calendar.google.com",
        "key": "AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs",
        "channel": 780959307403100181 if ENVIRONMENT == "prod" else 1104485755637735462,
    },
    {
        "name": "Stats 1 - May 23",
        "id": "c_p84m18r1paj8ccjlhdvtkj9sbk%40group.calendar.google.com",
        "key": "AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs",
        "channel": 780959569769660416 if ENVIRONMENT == "prod" else 1104485755637735460,
    },
    {
        "name": "CT - May 23",
        "id": "c_4uohcdlrfqd010amaomm03luso%40group.calendar.google.com",
        "key": "AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs",
        "channel": 780959847234535464 if ENVIRONMENT == "prod" else 1104485755864240260,
    },
]

# Tutorial to find calendar id and key -> https://www.loom.com/share/bc7029baab024b14a6a54d5cd6ec92cc?sid=341e7d29-15d3-4cb4-9420-354d5ed8cacf
