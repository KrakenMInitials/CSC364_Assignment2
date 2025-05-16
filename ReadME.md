KNOWN ISSUE: 

1. Never found a way to properly redraw input_prompt after a message is recieved. Refer to commit: 'implement prompt_toolkit failed' and 'ask_input() without 'prompt' package fail, will resort to using package'


### INFORMATION
You can run 'run.bat' to simulate, but otherwise use /server.py and /client.py in a regular client-server way.



User can leave Common, but the channel server-side will not be removed even when 0 users active in channel.

Said user will not be able to say anything in Common even if /switch succeeds until they've joined Common again.

- /list will show subscribed channels with a '*' and active channel with '(active)'
```
Existing channels:
   Common* (active)
   new_channel*
   newer_channel
```

- /join <channel> will update local copy of channels innately

Minor issue: 'Common' will always show up client-side as an existing channel because there is no way to confirm whether channel was removed on client leave.

Edge cases are handled both client-side and server-side.