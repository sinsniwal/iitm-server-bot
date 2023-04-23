# iitm-server-bot

This project is a Server Discord bot that handles interactions, messages, reactions, and email sending. It is built using Python and the Discord.py library.

## Getting Started

To use this bot, you need to do the following:

1. Clone this repository to your local machine.
2. Modify the `config.ini` file with your settings.
3. Install the required Python packages by running `pip install -r requirements.txt.`
4. Run the `main.py` file to start the bot.

## Project Structure

The project is structured as follows:

```
├── LICENSE
├── cogs
│   ├── Interaction.py
│   ├── Message.py
│   └── Reaction.py
├── config.ini
├── email_template.txt
├── main.py
├── requirements.txt
└── tools.py
```

- `LICENSE` contains the MIT License agreement for this project.
- `cogs` contains the Python files that handle the bot's functionalities.
- `config.ini` contains the settings for the bot. Modify this file with your settings.
- `email_template.txt` contains the template for the email that the bot sends.
- `main.py` is the main Python file that starts the bot and loads the different cogs.
- `requirements.txt` lists the required Python packages for the project.
- `tools.py` contains the code for sending emails and reading the `config.ini` file.

## Running the Bot

To run the bot, execute the following command:

```
python main.py
```

This command will start the bot and be ready to receive messages and interactions from Discord users.

## Contact

If you have any questions or suggestions, please feel free to contact me at mohit.sinsniwal.dev@gmail.com
