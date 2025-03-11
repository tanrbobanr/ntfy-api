from docs._misc.ext.utils import traverse_module, FQN, ObjType, FQNSelector
import time
import os
import re
import enum
import math
from typing import *

from src.ntfy_api._internals import URL


for v in sorted(FQNSelector.parse({  # see _misc.ext.utils.FQNSelector.parse
    "ntfy_api": {
        None: None,
        "enums": {
            (None, "__all__"): None,
            ("Tag", "HTTPMethod", "Event", "Priority"): False,
        },
        "subscription": {
            (None, "logger", "__all__"): None,
            "NtfySubscription": (
                "__post_init__",
                "_auth_header",
                "_thread",
                "_thread_fn",
                "_url",
                "_ws_conn",
            )
        },
        "message": {
            (None, "__all__"): None,
            "_ReceivedMessage": (
                "_parse_actions",
                "_parse_tags",
            ),
            "_Message": (
                "__init_subclass__",
                "_context",
                "_default_serializer",
                "_get_context",
                "_serialize",
            ),
            "Message": (
                "__post_init__",
                "_actions_serializer",
                "_ignore",
                "_tags_serializer",
            )
        },
        "filter": {
            (None, "__all__"): None,
            "_Filter": (
                "__init_subclass__",
                "_context",
                "_get_context",
                "_serialize",
                "_serializer",
            )
        },
        "errors": {
            (None, "__all__"): None,
            "APIError.__init__": None,
        },
        "creds": (
            None,
            "__all__",
            "Credentials._create_auth_header",
        ),
        "client": {
            (None, "__all__"): None,
            "NtfyClient": (
                "__post_init__",
                "_auth_header",
                "_http_client",
                "_url",
            )
        },
        "actions": {
            (None, "__all__"): None,
            "_Action": (
                "__init_subclass__",
                "_action",
                "_context",
                "_default_serializer",
                "_get_context",
                "_serialize",
            )
        },
        "_internals": {
            (None, "_SECURE_URL_SCHEMES", "StrTuple"): None,
            "WrappingDataclass": (
                "__init_subclass__",
                "_context",
                "_get_context",
            ),
            "URL._unparse": None,
            "ClearableQueue.queue": None,
        },
        "__package_info__": {
            (None, "__all__"): None,
            "_version_info": (
                "__copy__",
                "__deepcopy__",
                "__instance",
                "__new__",
            )
        }
    }
})):
    print(v)


# objects = set(traverse_module("src.ntfy_api", True))

# sels = tuple(FQNSelector.parse({
#     ("src", "ntfy_api"): {
#         "enums": {
#             "Tag": True,
#         }
#     }
# }))


# for sel in sels:
#     # for v in sel.get_matches(objects):
#     #     print(v)
#     objects.difference_update(set(sel.get_matches(objects)))

# for o in sorted(objects):
#     print(o)

# RawFQNSelection: TypeAlias = Union[
#     Mapping[Union[str, None], "RawFQNSelection"],
#     Sequence[str],
#     bool,
#     None
# ]


# def flatten_dict(d: FlattenableDict) -> Generator[
#     tuple[Union[str, bool, None], ...], None, None
# ]:
#     for k, v in d.items():
#         if isinstance(v, dict):
#             yield from ((k,) + v2 for v2 in flatten_dict(v))
#             continue
#         if k is None or v is None or isinstance(v, bool):
#             yield (k, v)
#             continue
#         yield from ((k, v2) for v2 in v)


# d = {
#     "ntfy_api": {
#         None: None,
#         "enums": {
#             "Tag": False,
#             "Event": False,
#             "HTTPMethod": True,
#         },
#         "client": [
#             "NtfyClient",
#             "__all__",
#         ],
#         "subscription": {
#             "NtfySubscription": None,
#             "__all__": None,
#         }
#     }
# }
# class FQNSelectionType(enum.Enum):
#     exact = "e"
#     members = "m"
#     root_and_members = "rm"


# class FQNSelection(tuple[str, ...]):
#     sel_type: FQNSelectionType

#     def __new__(
#         cls, sel_type: FQNSelectionType, iterable: Iterable[str] = ..., /
#     ) -> Self:
#         inst = super().__new__(cls, () if iterable is ... else iterable)
#         inst.sel_type = sel_type
#         return inst

#     def __repr__(self) -> str:
#         joined = ".".join(self)
#         return f"{joined}[{self.sel_type.value}]"

#     def prefix(self, prefix: Sequence[str]) -> Self:
#         return FQNSelection(
#             self.sel_type,
#             tuple(prefix) + self
#         )

#     @classmethod
#     def parse(cls, selection: RawFQNSelection) -> Generator[Self, None, None]:
#         # exact
#         if selection is None:
#             yield cls(FQNSelectionType.exact)
#             return

#         # members
#         if selection is False:
#             yield cls(FQNSelectionType.members)
#             return
            
#         # root and members
#         if selection is True:
#             yield cls(FQNSelectionType.root_and_members)
#             return

#         # sequence of exact matches
#         if isinstance(selection, Sequence):
#             for v in selection:
#                 yield cls(FQNSelectionType.exact, (v,))
#             return

#         # mapping of selections
#         for k, v in selection.items():
#             # referring to parent
#             if k is None:
#                 yield from cls.parse(v)
#                 continue

#             # k is FQN item and v is another raw FQN selection
#             for v2 in cls.parse(v):
#                 yield v2.prefix((k,))


# for v in FQNSelection.parse(d):
#     print(v)






    



# expected:
# - ntfy_api (exact)
# - ntfy_api.enums.Tag (members)
# - ntfy_api.enums.Event (members)
# - ntfy_api.enums.HTTPMethod (root and members)
# - ntfy_api.client.NtfyClient (exact)
# - ntfy_api.client.__all__ (exact)
# - ntfy_api.subscription.NtfySubscription (exact)
# - ntfy_api.subscription.__all__ (exact)


# x = {
#     "a": {
#         "b": {
#             None: None,
#             "c": [1, 2, 3, 4],
#             "d": {
#                 "e": [6, 7]
#             }
#         },
#         "f": [8, 9]
#     }
# }

# for v in flatten_dict(x):
#     print(v)


# print(URL.parse("https://www.example.co.uk:449/blog/article/search?docid=720&hi=en#dayone"))

# f = FQN(ObjType.v, ("src", "ntfy_api", "enums_x", "Tag", "sub", "_100"), has_docstring=True)




# print(f.matches("src.ntfy_api.enums_x.Tag.**"))


# for o in traverse_module("src.ntfy_api"):
#     if not o.matches("src.ntfy_api.enums.**"):
#         continue

#     if not o.matches("**.{Tag,Event,HTTPMethod,Priority}.*"):
#         print(o)



# print(len(list(traverse_module("src.ntfy_api", True))))


# class Printer:
#     # ANSI, non-ASCII, and characters that have complex behavior
#     remove_re = re.compile(
#         r"\033(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|[^ -~]"
#     )

#     def __init__(self, prefix: str) -> None:
#         self._prefix = self._strip(prefix)
#         self._prefix_w = len(self._prefix)
#         self._first_message: bool = True

#     @classmethod
#     def _strip(cls, value: str) -> str:
#         return cls.remove_re.sub("", value)

#     def _match_terminal_width()

#     def _get_text_height(self, stripped_text: str) -> int:
#         w, _ = os.get_terminal_size()
#         text_lines = (self._prefix + stripped_text).split("\n")
#         return sum(
#             (math.ceil(len(l) / w) - 1 for l in text_lines),
#             start=len(text_lines)
#         )

#     def __call__(self, message: str) -> None:
#         if self._first_message:
#             print("\033[A\033[G\033[J", end="")

#         stripped_msg = self._strip(message)
#         self._last_message_height = self._get_text_height(stripped_msg)

#         print(stripped_msg, flush=True, end="")

# import random
# import string

# p = Printer("Prog\nress: ")

# import tqdm

# for i in range(100):
#     time.sleep(0.2)
#     p("".join(random.sample(string.ascii_letters * 10, k=random.randint(1, 250))))



# print(Printer.remove_re.sub("", "abc\vdef"))
# print("abc\rdef")


    # def __call__(self, message: str, end: str = "\n") -> None:
        
    #     if self._first_message:
    #         print("\033[s", end="", flush=True)
    #         self._first_message = False
    #     else:
    #         print("\033[u\033[J", end="", flush=True)
    #     print(*values, flush=True, end="")

# print(os.get_terminal_size()[0])

# print("Progress: ", end="", flush=True)
# for v in traverse_module("src.ntfy_api", True):
#     # print(v)
#     time.sleep(0.001)
#     pass
    # print(v)
# print("bluddd")
# print("Progress: ", end="", flush=True)
# print("\033[s", end="", flush=True)
# print("abdefg", flush=True)
# time.sleep(2)
# print("\033[u", end="", flush=True)
# time.sleep(2)
# print("\033[J", end="", flush=True)
# time.sleep(2)
# print("hijklmnop")
# time.sleep(2)