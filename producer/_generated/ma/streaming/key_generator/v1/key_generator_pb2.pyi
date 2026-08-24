from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class KeyType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KEY_TYPE_UNSPECIFIED: _ClassVar[KeyType]
    KEY_TYPE_ULONG: _ClassVar[KeyType]
    KEY_TYPE_STRING: _ClassVar[KeyType]
KEY_TYPE_UNSPECIFIED: KeyType
KEY_TYPE_ULONG: KeyType
KEY_TYPE_STRING: KeyType

class GenerateUniqueKeyRequest(_message.Message):
    __slots__ = ("type",)
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: KeyType
    def __init__(self, type: _Optional[_Union[KeyType, str]] = ...) -> None: ...

class GenerateUniqueKeyResponse(_message.Message):
    __slots__ = ("string_key", "ulong_key")
    STRING_KEY_FIELD_NUMBER: _ClassVar[int]
    ULONG_KEY_FIELD_NUMBER: _ClassVar[int]
    string_key: str
    ulong_key: int
    def __init__(self, string_key: _Optional[str] = ..., ulong_key: _Optional[int] = ...) -> None: ...
