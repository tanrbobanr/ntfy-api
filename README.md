A Python wrapper around the [ntfy](https://ntfy.sh) API.

# Install
`$ pip install ntfy-api`

# Usage
This package is in its early stages, and currently only supports sending
messages:
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
