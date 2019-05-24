from collections import defaultdict
from functools import partial
import json
import re

from discord.ext import commands
from discord.ext.commands.converter import _get_from_guilds, BadArgument

import parsing


class CommandError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_cog(Commands(self))

    async def on_message(self, msg):
        ctx = await self.get_context(msg)
        await self.invoke(ctx)

    async def on_command_error(self, ctx, exception):
        await ctx.send(exception)


class Commands:
    def __init__(self, bot):
        self.bot = bot
        self.commands = defaultdict(dict)

        with open("savedata.json") as sd:
            data = json.load(sd)
        self.userdata = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
        self.commands = defaultdict(dict)
        for gid, item in data['data'].items():
            self.userdata[gid] = defaultdict(lambda: None)
            self.userdata[gid].update(item)

        for gid, item in data['commands'].items():
            self.commands[gid].update(item)

        self._id_regex = re.compile(r'([0-9]{15,21})$')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def logout(self, ctx):
        with open("savedata.json", "w") as sd:
            json.dump({'commands': self.commands, 'data': self.userdata}, sd, indent=4)
        await ctx.bot.logout()

    @commands.command()
    async def create(self, ctx, name, *, args):
        """Create a new command.
        The name will be the name of the command, which is used to invoke the command
        The arguments are the names of the arguments which will be passed to the command
        All code is valid Python, so write like its Python

        For example: `r!create target user`
        This will begin the creation of a command called "target", whose only argument is the "user"
        You will then be prompted for the body of the command as follows

        Henry: r!create target user
        Bot: What will the body of the command be?
        Henry: targetmember = getmember(user)
               setdata(author, "targeting", targetmember)
               reply("Now targeting " + (name(targetmember)))
        Bot: Command created!

        There are a number of variables which are used here.
        First is the `user` variable. This is the first argument which will be passed by the user
        If the user invokes the command by typing `r!run target @Henry#6174`, user will be
        @Henry6174's user ID.

        Otherwise, there are many other variables which will be defined as follows:
            Command Specific:
            - author : The ID of the author of the message (an integer)
            - channel : The ID of the channel of the message
            - content : The original content of the message

            Functions:
            - if : The if function is used to simulate an if statement:
                   There are three arguments: the condition, the True value, and the False value
                   For example: `val = if(num == 5, "Five", "Not five")`
                   If num is equal to 5, val will be "Five", otherwise it will be "Not five"
            - getdata : All data is stored specific to the server. If you want to get a specific
                        key from that servers data, use `val = getdata(userid, "health")`. This will return
                        None if there is no value for "health" there. Otherwise, you may add an additional argument
                        `val = getdata(userid, "health", 30)` This will return 30 health, if health hasn't been defined yet.
                        The first argument may either be an ID (int) or a string.
            - setdata : The same as getdata but backwards. `setdata(userid, "health", 10)` will set the key
                        "health" for the user to 10. The first argument may be an int or a string.
            - getmember : Get the member ID from a mention. For example if a user inputs @Henry#6174, it will turn that
                          into the user's ID.
            - reply : To reply in the current channel, use the reply function. This takes as many arguments as you
                      would like and separates them with spaces. For example `reply(name(user) + " has died!")` is
                      the same as `reply(name(user), "has", "died!")`
            - name : Return the display name of a member given their ID. For example `name(user)` or `name(getmember(mention))`
            - end : End the command without executing the rest, responding with a message.
                    For example: `end("Cannot attack! You are not targeting anyone!")`

            Other things:
            - Math stuff available : sin(), cos(), tan(), asin(), acos(), atan(), atan2(), pi
            - Random : rand(), returns a number between 0 (inclusive) and 1 (exclusive)
            - Type conversions : int(), float(), str()
            - None : None, a type representing nothing, and nil, a function that does nothing with any number of args.
                     Useful for logic: `if(target == None, end, nil)("You aren't targeting anyone!")`
                     This will stop execution if target is equal to None, otherwise it will do nothing.

        """
        args = args.split()
        await ctx.send("What will the body of the command be?")
        msg = await ctx.bot.wait_for("message",
                                     check=lambda x: x.channel == ctx.channel and x.author == ctx.author,
                                     timeout=60 * 5)
        if msg.content.lower() == "cancel":
            return
        else:
            body = msg.content

        self.commands[str(ctx.guild.id)][name] = (args, body)
        await ctx.send("Command created!")

    @commands.command()
    async def run(self, ctx, name, *args):
        cmdargs, body = self.commands[str(ctx.guild.id)][name]
        messages = []
        parsing.uvars = {
            "author": ctx.author.id,
            "content": ctx.message.content,
            "channelid": ctx.channel.id,
            "if": self.iffunc,
            "getdata": partial(self.getdata, ctx),
            "setdata": partial(self.setdata, ctx),
            "getmember": lambda x: self.convert(ctx, x).id,
            "reply": lambda *x: messages.append(" ".join(x)),
            "name": lambda x: ctx.guild.get_member(x).display_name,
            "end": partial(self.end, ctx)
        }
        parsing.uvars.update(parsing.cvars)
        if len(args) != len(cmdargs):
            raise ValueError("Didn't provide enough arguments!")
        parsing.uvars.update(zip(cmdargs, args))

        try:
            parsing.getparser().parse(body)
        except CommandError as e:
            await ctx.send(e.message)

        for message in messages:
            await ctx.send(message)

    def convert(self, ctx, argument):
        message = ctx.message
        bot = ctx.bot
        match = self._id_regex.match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
        guild = message.guild
        result = None
        if match is None:
            # not a mention...
            if guild:
                result = guild.get_member_named(argument)
            else:
                result = _get_from_guilds(bot, 'get_member_named', argument)
        else:
            user_id = int(match.group(1))
            if guild:
                result = guild.get_member(user_id)
            else:
                result = _get_from_guilds(bot, 'get_member', user_id)

        if result is None:
            raise BadArgument('Member "{}" not found'.format(argument))

        return result

    def iffunc(self, condition, do, other):
        return do if condition else other

    def getdata(self, ctx, user, name, default=None):
        if not isinstance(user, (int, str)):
            raise ValueError("Can only getdata for user IDs or strings")
        return self.userdata[str(ctx.guild.id)][str(user)].get(name, default)  # .id][name]

    def setdata(self, ctx, user, name, value):
        if not isinstance(user, (int, str)):
            raise ValueError("Can only setdata for user IDs or strings")
        self.userdata[str(ctx.guild.id)][str(user)][name] = value  # .id][name]

    def end(self, ctx, message):
        raise CommandError(message)


bot = Bot(command_prefix="r!", description="TBA")
bot.run(open("auth").read())
