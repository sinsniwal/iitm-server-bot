# IITM-Server-Bot

This project is a Server Discord bot that handles interactions, messages, reactions, and Slash commands. It is built using Python and the Discord.py library.


## Setup for Running the Bot

To use this bot, you need to do the following:

1. Clone this repository to your local machine.
2. Modify `config.py` with your settings.
3. Add the required secrets to `.env.example`
4. Rename `.env.example` to `.env`
5. Install the required Python packages by running `pip install -r requirements.txt.`
6. Run the `main.py` file to start the bot.

## Setup for Development
1. Clone this repository to your local machine.
2. Modify `config.py` with your settings.
3. Add the required secrets to `.env.example`
4. Rename `.env.example` to `.env`
5. Install `poetry` using `pip install poetry`
6. Install the required python packages by running `poetry install`
7. Run the `main.py` file to start the bot.

### Commonly used poetry commands
- **Adding Dependency** `poetry add <package_name>`
- **Adding Dev Dependency** `poetry add <package_name> --group dev`
- **Updating Requirements File** `poetry export --without-hashes --only main -o requirements.txt`
- **Updating Dev Requirements File** `poetry export --without-hashes -o dev-requirements.txt --with dev`

## Project Structure

The project is structured as follows:

```
.
├── .github
│   └── workflows
│       └── phraseActions.yml
├── cogs
│   ├── dev.py
│   ├── interaction.py
│   ├── reaction.py
│   ├── slash.py
│   └── verification.py
├── utils
│   ├── email_template.txt
│   └── helper.py
├── .gitignore
├── LICENSE
├── README.md
├── bot.py
├── config.py
├── main.py
├── .env
└── requirements.txt
```

### `.github`
It is a convention to keep all GitHub-related stuff inside the folder used. It houses workflows, issue templates, pull request templates, funding information, codeowners, SECURITY.md, and other files specific to that project. All folders starting from `.` are hidden by default in most Linux desktop environments' file managers.

### `workflows`
All GitHub workflows reside here
Refer to these pages from GitHub docs:
- [Using workflows](https://docs.github.com/en/actions/using-workflows)
- [About workflows](https://docs.github.com/en/actions/using-workflows/about-workflows)

### `workflows/phraseActions.yml`
Contains the workflows which act as a bot listening for slash commands.

### `cogs`
Contains the Python files that handle the bot's functionalities.

### `LICENSE`
Contains the MIT License agreement for this project.

### `README.md`
This file which you are reading right now.

### `config.py`
All _Non-Sensitive_ global config variables are set here for the bot.

### `.env`
All _Sensitive_ variables such as discord tokens and other secrets.
````
DISCORD_BOT_TOKEN="PASTE BOT TOKEN HERE"
SIB_API_KEY="PASTE API KEY HERE"
SIB_SENDER_EMAIL="PLACE EMAIL HERE"
FERNET="PLACE FERNET KEY HERE"
````

### `utils/email_template.txt`
Contains the template for the email that the bot sends.

### `main.py`
The main Python file starts the bot and loads the different cogs. It reads environment variables to start the bot by importing IITMBot from bot.py and sets it up along with the context manager for logging.

### `requirements.txt`
It is the list of required Python packages for the project.

### `cogs/dev.py`
Contains commands for development purposes. All these commands require the `is_owner` decorator to limit their use to just the bot owner.
- `!eval` - Useful to run code on the fly to test stuff. (Dangerous when abused)
- `!kill` - Kill the bot through discord
- `!sync_apps` - Synchronize slash commands to the bot
- `!clear_apps` - Remove all slash commands from the bot

### `cogs/verification.py`
Contains code for verification of new joiners.


## Running The Bot

To run the bot, execute the following command:

```
python main.py
```

This command will start the bot and be ready to receive messages and interactions from Discord users.


## Contact

If you have any questions or suggestions, please feel free to contact the repo owner at mohit.sinsniwal.dev@gmail.com

Alternatively, you can contact other developers via the [Discord Server](https://discord.gg/iitm-bs-students-762774569827565569). Search for people with the `developer` role.
