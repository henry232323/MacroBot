from collections import defaultdict

import parsing

userdata = defaultdict(defaultdict)
userdata["Dan"]["health"] = 30


def iffunc(condition, do, other):
    return do if condition else other


def getdata(user, name, default=None):
    # if not isinstance(user, discord.User):
    #    raise
    return userdata[user].get(name, default)  # .id][name]

def end(msg):
    raise Exception(msg)


def setdata(user, name, value):
    # if not isinstance(user, discord.User):
    #    raise
    userdata[user][name] = value  # .id][name]


def getuser(userid):
    return userid
    return ctx.guild.get_user(userid)


parsing.uvars = {
    "author": "Henry",
    "if": iffunc,
    "getdata": getdata,
    "setdata": setdata,
    "getmember": getuser,
    "end": end,
    "reply": print,
    "name": lambda x: "Henry",

    "targeted": "Dan",
    "type": "a",
    "amount": 30,
    "targetid": "Dan"
}
parsing.uvars.update(parsing.cvars)

commands = """
print( 
    "DSA"
)

print(author)
"""

# rp!target @XUser
# @target "shinobi kantos" @reflex 1d20+ @base attack
target = """
setdata(author, "targeting", targeted)
reply("Now targeting " + (name(targeted)))
"""

# rp!attack type 20
attack = """
damage = if(type == "d", int(amount), int(rand() * (int(amount)))) 

target = getdata(author, "targeting", None)
if(target == None, end, nil)("You aren't targeting anyone!")
health = getdata(target, "health", 30)
reply(name(target) + " took " + (str(damage)) + " damage.")
damage = if(damage > health, health, damage)
setdata(target, "health", health - damage)

if(health == damage, reply, nil)(name(target) + " has died!")
"""

parsing.getparser().parse(target)
parsing.getparser().parse(attack)
parsing.getparser().parse(attack)
