# MacroBot
A bot that provides custom macro commands


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
### Command Specific:
- author : The ID of the author of the message (an integer)
- channel : The ID of the channel of the message
- content : The original content of the message

### Functions:
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

### Other things:
- Math stuff available : sin(), cos(), tan(), asin(), acos(), atan(), atan2(), pi
- Random : rand(), returns a number between 0 (inclusive) and 1 (exclusive)
- Type conversions : int(), float(), str()
- None : None, a type representing nothing, and nil, a function that does nothing with any number of args.
         Useful for logic: `if(target == None, end, nil)("You aren't targeting anyone!")`
         This will stop execution if target is equal to None, otherwise it will do nothing.
