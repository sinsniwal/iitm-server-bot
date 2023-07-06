# Nothing in this file is evaluated at runtime
# These are convenience classes and type aliases that make Pyright happy
# And specialize some generic types provided by discord.py


from discord.ext import commands

from bot import IITMBot


class Context(commands.Context[IITMBot]):
    """
    A :class:`commands.Context` belonging to an :class:`IITMBot`.
    """

    ...
