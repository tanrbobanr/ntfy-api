API Reference
=============

This page contains the full reference to this package's API.

Classes
-------

.. autoclass:: ntfy_api.actions.BroadcastAction
    :show-inheritance:

    .. autoivar:: label

    .. autoivar:: intent

    .. autoivar:: extras

    .. autoivar:: clear

    .. automethod:: serialize


.. autoclass:: ntfy_api.creds.Credentials

    .. autoivar:: basic

    .. autoivar:: bearer

    .. automethod:: get_header


.. autoclass:: ntfy_api.enums.Event()
    :show-inheritance:


.. autoclass:: ntfy_api.filter.Filter
    :show-inheritance:

    .. autoivar:: id

    .. autoivar:: message

    .. autoivar:: priority

    .. autoivar:: scheduled

    .. autoivar:: since

    .. autoivar:: tags

    .. autoivar:: title

    .. automethod:: serialize


.. autoclass:: ntfy_api.actions.HTTPAction
    :show-inheritance:

    .. autoivar:: label

    .. autoivar:: url

    .. autoivar:: method

    .. autoivar:: headers

    .. autoivar:: body

    .. autoivar:: clear

    .. automethod:: serialize


.. autoclass:: ntfy_api.enums.HTTPMethod()
    :show-inheritance:


.. autoclass:: ntfy_api.message.Message
    :show-inheritance:

    .. autoivar:: topic

    .. autoivar:: message

    .. autoivar:: title

    .. autoivar:: priority

    .. autoivar:: tags

    .. autoivar:: markdown

    .. autoivar:: delay

    .. autoivar:: templating

    .. autoivar:: actions

    .. autoivar:: click

    .. autoivar:: attachment

    .. autoivar:: filename

    .. autoivar:: icon

    .. autoivar:: email

    .. autoivar:: call

    .. autoivar:: cache

    .. autoivar:: firebase

    .. autoivar:: unified_push

    .. autoivar:: data

    .. automethod:: get_args


.. autoclass:: ntfy_api.client.NtfyClient

    .. autoivar:: base_url

    .. autoivar:: default_topic

    .. autoivar:: credentials

    .. automethod:: connect

    .. automethod:: close

    .. automethod:: publish

    .. automethod:: poll

    .. automethod:: subscribe

    .. automethod:: __enter__

    .. automethod:: __exit__


.. autoclass:: ntfy_api.subscription.NtfySubscription

    .. autoivar:: base_url

    .. autoivar:: credentials

    .. autoivar:: filter

    .. autoivar:: max_queue_size

    .. autoivar:: messages

    .. autoivar:: topics

    .. automethod:: close

    .. automethod:: connect

    .. automethod:: __enter__

    .. automethod:: __exit__


.. autoclass:: ntfy_api.enums.Priority()
    :show-inheritance:


.. autoclass:: ntfy_api.message.ReceivedAttachment
    :show-inheritance:

    .. autoivar:: expires

    .. autoivar:: name

    .. autoivar:: size

    .. autoivar:: type

    .. autoivar:: url


.. autoclass:: ntfy_api.actions.ReceivedBroadcastAction
    :show-inheritance:

    .. autoivar:: id

    .. autoivar:: label

    .. autoivar:: clear

    .. autoivar:: intent

    .. autoivar:: extras

    .. automethod:: from_json


.. autoclass:: ntfy_api.actions.ReceivedHTTPAction()
    :show-inheritance:

    .. autoivar:: id

    .. autoivar:: label

    .. autoivar:: url

    .. autoivar:: clear

    .. autoivar:: method

    .. autoivar:: headers

    .. autoivar:: body

    .. automethod:: from_json


.. autoclass:: ntfy_api.message.ReceivedMessage()
    :show-inheritance:

    .. autoivar:: actions

    .. autoivar:: attachment

    .. autoivar:: click

    .. autoivar:: content_type

    .. autoivar:: event

    .. autoivar:: expires

    .. autoivar:: icon

    .. autoivar:: id

    .. autoivar:: message

    .. autoivar:: priority

    .. autoivar:: tags

    .. autoivar:: time

    .. autoivar:: title

    .. autoivar:: topic


.. autoclass:: ntfy_api.actions.ReceivedViewAction
    :show-inheritance:

    .. autoivar:: id

    .. autoivar:: label

    .. autoivar:: url

    .. autoivar:: clear

    .. automethod:: from_json


.. autoclass:: ntfy_api.enums.Tag()
    :show-inheritance:


.. autoclass:: ntfy_api.actions.ViewAction
    :show-inheritance:

    .. autoivar:: label

    .. autoivar:: url

    .. autoivar:: clear

    .. automethod:: serialize

Constants
---------

.. autodata:: ntfy_api.__version__.__author__


.. autodata:: ntfy_api.__version__.__author_email__


.. autodata:: ntfy_api.__version__.__cookie__


.. autodata:: ntfy_api.__version__.__copyright__


.. autodata:: ntfy_api.__version__.__description__


.. autodata:: ntfy_api.__version__.__download_url__


.. autodata:: ntfy_api.__version__.__email__


.. autodata:: ntfy_api.__version__.__license__


.. autodata:: ntfy_api.__version__.__title__


.. autodata:: ntfy_api.__version__.__url__


.. autodata:: ntfy_api.__version__.__version__


.. autodata:: ntfy_api.__version__.__release__


.. autodata:: ntfy_api.__version__.version_info

Exceptions
----------

.. autoexception:: ntfy_api.errors.APIError

Type aliases
------------

.. autoalias:: ntfy_api.actions.ReceivedAction
