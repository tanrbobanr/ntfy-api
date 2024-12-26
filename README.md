A Python wrapper around the [ntfy](https://ntfy.sh) API.

# Install
`$ pip install ntfy-api`

# Usage
This package supports sending and receiving messages. Here is an example of how to send a message:

```py
from ntfy_api import *


# create NtfyPublisher instance
ntfy_pub = NtfyPublisher("https://ntfy.example.com", basic=..., bearer=...)

# create message
msg = Message(
    topic="my-topic",
    message="**Hello World**",
    title="Super Cool Message",
    priority=Priority.urgent, # or just `5`
    tags=[Tag._100], # or just `["100"]`
    markdown=True,
    delay="10m",
    actions=[
        ViewAction(label="GOOGLE", url="https://google.com"),
        BroadcastAction(
            label="Take picture",
            extras={"cmd": "pic", "camera": "front"}
        )
    ],
    click="https://youtube.com",
    attach="https://docs.ntfy.sh/static/img/ntfy.png",
    filename="ntfy.png",
    icon="https://ntfy.sh/_next/static/media/logo.077f6a13.svg"
)

# send message
ntfy_pub.publish(msg)

# OR

ntfy_pub << msg
```

For polling or subscribing:

```py
from ntfy_api import *


# create NtfyPublisher instance
ntfy_sub = NtfySubscriber("https://ntfy.example.com", topic="your-topic", basic=..., bearer=...)

# poll messages or subscribe by replacing poll() with subscribe()
for message in ntfy_sub.poll():
    if message and message.event == "message":
        print('>> Message received <<')
        print(f'Title: {message.title}')
        print(f'Message: {message.message}')
        print(f'Click: {message.click}')
        if message.attachment:
            att = message.attachment
            print(f'Attachments: {att}')
    else:
        print(message)
```
