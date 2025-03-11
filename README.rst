.. raw:: html

    <div align="center">
    <h1>ntfy-api</h1>


A Python wrapper around the `ntfy <https://ntfy.sh>`__ API.


.. |DOCS| replace:: **Explore the docs »**
.. _DOCS: https://docs.tannercorcoran.dev/python/ntfy-api

|DOCS|_


.. image:: https://img.shields.io/badge/tests-passing-_
    :target: `Tests and Coverage Policies`_
    :alt: Tests: passing

.. image:: https://img.shields.io/badge/coverage-100%25-_
    :target: `Tests and Coverage Policies`_
    :alt: Coverage: 100%

.. image:: https://img.shields.io/pypi/l/ntfy-api?color=purple
    :target: https://github.com/tanrbobanr/ntfy-api/blob/main/LICENSE
    :alt: License: Apache 2.0

.. image:: https://img.shields.io/pypi/v/ntfy-api?color=blue
    :target: https://pypi.org/project/ntfy-api
    :alt: PyPI

.. image:: https://static.pepy.tech/badge/ntfy-api
    :target: https://pypi.org/project/ntfy-api
    :alt: Downloads

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code style: black


.. raw:: html

   </div>


Install
-------

``$ pip install ntfy-api``


Usage
-----

This package supports sending and receiving messages. Here is an example
of how to send a message:

.. code:: python

    import ntfy_api

    # create a client
    client = ntfy_api.NtfyClient(
        base_url="https://www.example.com",
        credentials=ntfy_api.Credentials(...), # if authorization is needed
    )

    # create a message
    msg = Message(
        topic="my-topic",
        message="**Hello World**",
        title="Super Cool Message",
        priority=Priority.urgent, # or `5`
        tags=[Tag._100], # or `["100"]`
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
        filename="ntfy_api.png",
        icon="https://ntfy.sh/_next/static/media/logo.077f6a13.svg"
    )

    # send message
    client.publish(msg)

For polling or subscribing:

.. code:: python

    # poll messages
    for msg in client.poll("my-topic"):
        print('>> Message received <<')
        print(f'Title: {msg.title}')
        print(f'Message: {msg.message}')
        print(f'Click: {msg.click}')
        if msg.attachment:
            print(f'Attachments: {msg.attachment}')

    # subscribe
    with client.subscribe("my-topic") as subscription:
        msg = subscription.messages.get()
        print('>> Message received <<')
        print(f'Title: {msg.title}')
        print(f'Message: {msg.message}')
        print(f'Click: {msg.click}')
        if msg.attachment:
            print(f'Attachments: {msg.attachment}')


Tests and Coverage Policies
---------------------------

This project does not have coverage reports or test results available.
As part of the release process, full (100%) code coverage is required,
and all tests must pass for all supported versions on all major operating
systems.
