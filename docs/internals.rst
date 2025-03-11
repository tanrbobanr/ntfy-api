Internals Reference
===================

This page contains reference to this package's internals.

Classes
-------

.. autoclass:: ntfy_api.__version__._version_info
    :show-inheritance:

    .. autoproperty:: major

    .. autoproperty:: minor

    .. autoproperty:: micro

    .. autoproperty:: pre

    .. autoproperty:: post

    .. autoproperty:: dev

    .. automethod:: version_str

    .. automethod:: release_str


.. autoclass:: ntfy_api.actions._Action

    .. automethod:: serialize


.. autoclass:: ntfy_api.filter._Filter

    .. automethod:: serialize


.. autoclass:: ntfy_api.message._Message

    .. automethod:: serialize


.. autoclass:: ntfy_api.message._ReceivedAttachment
    :show-inheritance:

    .. autoivar:: expires

    .. autoivar:: name

    .. autoivar:: size

    .. autoivar:: type

    .. autoivar:: url


.. autoclass:: ntfy_api.message._ReceivedMessage
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


.. autoclass:: ntfy_api._internals.URL

    .. autoivar:: scheme

    .. autoivar:: netloc

    .. autoivar:: path

    .. autoivar:: params

    .. autoivar:: query

    .. autoivar:: fragment

    .. automethod:: parse

    .. automethod:: unparse


.. autoclass:: ntfy_api._internals.WrappingDataclass

    .. automethod:: from_json


.. autoclass:: ntfy_api._internals.ClearableQueue
    :show-inheritance:

    .. automethod:: clear

Type Variables
--------------

.. autotvar:: ntfy_api._internals._T
