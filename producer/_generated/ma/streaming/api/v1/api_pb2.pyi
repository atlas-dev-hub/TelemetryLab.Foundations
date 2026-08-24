import datetime

from ma.streaming.open_data.v1 import open_data_pb2 as _open_data_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InfoType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INFO_TYPE_UNSPECIFIED: _ClassVar[InfoType]
    INFO_TYPE_SESSION_INFO: _ClassVar[InfoType]
    INFO_TYPE_SYSTEM_STATUS: _ClassVar[InfoType]
INFO_TYPE_UNSPECIFIED: InfoType
INFO_TYPE_SESSION_INFO: InfoType
INFO_TYPE_SYSTEM_STATUS: InfoType

class DataPacketDetails(_message.Message):
    __slots__ = ("message", "data_source", "stream", "session_key")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    message: _open_data_pb2.Packet
    data_source: str
    stream: str
    session_key: str
    def __init__(self, message: _Optional[_Union[_open_data_pb2.Packet, _Mapping]] = ..., data_source: _Optional[str] = ..., stream: _Optional[str] = ..., session_key: _Optional[str] = ...) -> None: ...

class WriteDataPacketRequest(_message.Message):
    __slots__ = ("detail",)
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    detail: DataPacketDetails
    def __init__(self, detail: _Optional[_Union[DataPacketDetails, _Mapping]] = ...) -> None: ...

class WriteDataPacketsRequest(_message.Message):
    __slots__ = ("details",)
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    details: _containers.RepeatedCompositeFieldContainer[DataPacketDetails]
    def __init__(self, details: _Optional[_Iterable[_Union[DataPacketDetails, _Mapping]]] = ...) -> None: ...

class WriteInfoPacketRequest(_message.Message):
    __slots__ = ("message", "type")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    message: _open_data_pb2.Packet
    type: InfoType
    def __init__(self, message: _Optional[_Union[_open_data_pb2.Packet, _Mapping]] = ..., type: _Optional[_Union[InfoType, str]] = ...) -> None: ...

class WriteInfoPacketsRequest(_message.Message):
    __slots__ = ("message", "type")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    message: _open_data_pb2.Packet
    type: InfoType
    def __init__(self, message: _Optional[_Union[_open_data_pb2.Packet, _Mapping]] = ..., type: _Optional[_Union[InfoType, str]] = ...) -> None: ...

class WriteDataPacketResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WriteDataPacketsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WriteInfoPacketResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WriteInfoPacketsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetParameterDataFormatIdRequest(_message.Message):
    __slots__ = ("data_source", "parameters")
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    parameters: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, data_source: _Optional[str] = ..., parameters: _Optional[_Iterable[str]] = ...) -> None: ...

class GetParameterDataFormatIdResponse(_message.Message):
    __slots__ = ("data_format_identifier",)
    DATA_FORMAT_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    data_format_identifier: int
    def __init__(self, data_format_identifier: _Optional[int] = ...) -> None: ...

class GetEventDataFormatIdRequest(_message.Message):
    __slots__ = ("data_source", "event")
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    event: str
    def __init__(self, data_source: _Optional[str] = ..., event: _Optional[str] = ...) -> None: ...

class GetEventDataFormatIdResponse(_message.Message):
    __slots__ = ("data_format_identifier",)
    DATA_FORMAT_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    data_format_identifier: int
    def __init__(self, data_format_identifier: _Optional[int] = ...) -> None: ...

class GetParametersListRequest(_message.Message):
    __slots__ = ("data_source", "data_format_identifier")
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    DATA_FORMAT_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    data_format_identifier: int
    def __init__(self, data_source: _Optional[str] = ..., data_format_identifier: _Optional[int] = ...) -> None: ...

class GetParametersListResponse(_message.Message):
    __slots__ = ("parameters",)
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    parameters: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, parameters: _Optional[_Iterable[str]] = ...) -> None: ...

class GetEventRequest(_message.Message):
    __slots__ = ("data_source", "data_format_identifier")
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    DATA_FORMAT_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    data_format_identifier: int
    def __init__(self, data_source: _Optional[str] = ..., data_format_identifier: _Optional[int] = ...) -> None: ...

class GetEventResponse(_message.Message):
    __slots__ = ("event",)
    EVENT_FIELD_NUMBER: _ClassVar[int]
    event: str
    def __init__(self, event: _Optional[str] = ...) -> None: ...

class Connection(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class ConnectionDetails(_message.Message):
    __slots__ = ("data_source", "session_key", "streams", "stream_offsets", "main_offset", "essentials_offset", "exclude_main_stream", "consumer_group")
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    STREAMS_FIELD_NUMBER: _ClassVar[int]
    STREAM_OFFSETS_FIELD_NUMBER: _ClassVar[int]
    MAIN_OFFSET_FIELD_NUMBER: _ClassVar[int]
    ESSENTIALS_OFFSET_FIELD_NUMBER: _ClassVar[int]
    EXCLUDE_MAIN_STREAM_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_GROUP_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    session_key: str
    streams: _containers.RepeatedScalarFieldContainer[str]
    stream_offsets: _containers.RepeatedScalarFieldContainer[int]
    main_offset: int
    essentials_offset: int
    exclude_main_stream: bool
    consumer_group: str
    def __init__(self, data_source: _Optional[str] = ..., session_key: _Optional[str] = ..., streams: _Optional[_Iterable[str]] = ..., stream_offsets: _Optional[_Iterable[int]] = ..., main_offset: _Optional[int] = ..., essentials_offset: _Optional[int] = ..., exclude_main_stream: bool = ..., consumer_group: _Optional[str] = ...) -> None: ...

class NewConnectionRequest(_message.Message):
    __slots__ = ("details",)
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    details: ConnectionDetails
    def __init__(self, details: _Optional[_Union[ConnectionDetails, _Mapping]] = ...) -> None: ...

class NewConnectionResponse(_message.Message):
    __slots__ = ("connection",)
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    connection: Connection
    def __init__(self, connection: _Optional[_Union[Connection, _Mapping]] = ...) -> None: ...

class GetConnectionRequest(_message.Message):
    __slots__ = ("connection",)
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    connection: Connection
    def __init__(self, connection: _Optional[_Union[Connection, _Mapping]] = ...) -> None: ...

class GetConnectionResponse(_message.Message):
    __slots__ = ("details",)
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    details: ConnectionDetails
    def __init__(self, details: _Optional[_Union[ConnectionDetails, _Mapping]] = ...) -> None: ...

class CloseConnectionRequest(_message.Message):
    __slots__ = ("connection",)
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    connection: Connection
    def __init__(self, connection: _Optional[_Union[Connection, _Mapping]] = ...) -> None: ...

class CloseConnectionResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class ReadPacketsRequest(_message.Message):
    __slots__ = ("connection",)
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    connection: Connection
    def __init__(self, connection: _Optional[_Union[Connection, _Mapping]] = ...) -> None: ...

class ReadPacketsResponse(_message.Message):
    __slots__ = ("response",)
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: _containers.RepeatedCompositeFieldContainer[PacketResponse]
    def __init__(self, response: _Optional[_Iterable[_Union[PacketResponse, _Mapping]]] = ...) -> None: ...

class ReadEssentialsRequest(_message.Message):
    __slots__ = ("connection",)
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    connection: Connection
    def __init__(self, connection: _Optional[_Union[Connection, _Mapping]] = ...) -> None: ...

class ReadEssentialsResponse(_message.Message):
    __slots__ = ("response",)
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: _containers.RepeatedCompositeFieldContainer[PacketResponse]
    def __init__(self, response: _Optional[_Iterable[_Union[PacketResponse, _Mapping]]] = ...) -> None: ...

class ReadDataPacketsRequest(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: DataPacketRequest
    def __init__(self, request: _Optional[_Union[DataPacketRequest, _Mapping]] = ...) -> None: ...

class ReadDataPacketsResponse(_message.Message):
    __slots__ = ("response",)
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: _containers.RepeatedCompositeFieldContainer[PacketResponse]
    def __init__(self, response: _Optional[_Iterable[_Union[PacketResponse, _Mapping]]] = ...) -> None: ...

class DataPacketRequest(_message.Message):
    __slots__ = ("connection", "include_parameters", "exclude_parameters", "include_events", "exclude_events", "include_markers")
    CONNECTION_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    EXCLUDE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EVENTS_FIELD_NUMBER: _ClassVar[int]
    EXCLUDE_EVENTS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_MARKERS_FIELD_NUMBER: _ClassVar[int]
    connection: Connection
    include_parameters: _containers.RepeatedScalarFieldContainer[str]
    exclude_parameters: _containers.RepeatedScalarFieldContainer[str]
    include_events: _containers.RepeatedScalarFieldContainer[str]
    exclude_events: _containers.RepeatedScalarFieldContainer[str]
    include_markers: bool
    def __init__(self, connection: _Optional[_Union[Connection, _Mapping]] = ..., include_parameters: _Optional[_Iterable[str]] = ..., exclude_parameters: _Optional[_Iterable[str]] = ..., include_events: _Optional[_Iterable[str]] = ..., exclude_events: _Optional[_Iterable[str]] = ..., include_markers: bool = ...) -> None: ...

class PacketResponse(_message.Message):
    __slots__ = ("packet", "stream", "submit_time")
    PACKET_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    SUBMIT_TIME_FIELD_NUMBER: _ClassVar[int]
    packet: _open_data_pb2.Packet
    stream: str
    submit_time: _timestamp_pb2.Timestamp
    def __init__(self, packet: _Optional[_Union[_open_data_pb2.Packet, _Mapping]] = ..., stream: _Optional[str] = ..., submit_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateSessionRequest(_message.Message):
    __slots__ = ("data_source", "type", "version", "utc_offset", "identifier", "associate_session_key", "details", "creation_time")
    class DetailsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UTC_OFFSET_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIME_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    type: str
    version: int
    utc_offset: _duration_pb2.Duration
    identifier: str
    associate_session_key: _containers.RepeatedScalarFieldContainer[str]
    details: _containers.ScalarMap[str, str]
    creation_time: _timestamp_pb2.Timestamp
    def __init__(self, data_source: _Optional[str] = ..., type: _Optional[str] = ..., version: _Optional[int] = ..., utc_offset: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., identifier: _Optional[str] = ..., associate_session_key: _Optional[_Iterable[str]] = ..., details: _Optional[_Mapping[str, str]] = ..., creation_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateSessionResponse(_message.Message):
    __slots__ = ("session_key", "new_session", "success")
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    NEW_SESSION_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    session_key: str
    new_session: _open_data_pb2.NewSessionPacket
    success: bool
    def __init__(self, session_key: _Optional[str] = ..., new_session: _Optional[_Union[_open_data_pb2.NewSessionPacket, _Mapping]] = ..., success: bool = ...) -> None: ...

class EndSessionRequest(_message.Message):
    __slots__ = ("data_source", "session_key", "termination_time")
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_TIME_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    session_key: str
    termination_time: _timestamp_pb2.Timestamp
    def __init__(self, data_source: _Optional[str] = ..., session_key: _Optional[str] = ..., termination_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class EndSessionResponse(_message.Message):
    __slots__ = ("end_session", "success")
    END_SESSION_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    end_session: _open_data_pb2.EndOfSessionPacket
    success: bool
    def __init__(self, end_session: _Optional[_Union[_open_data_pb2.EndOfSessionPacket, _Mapping]] = ..., success: bool = ...) -> None: ...

class GetCurrentSessionsRequest(_message.Message):
    __slots__ = ("data_source",)
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    def __init__(self, data_source: _Optional[str] = ...) -> None: ...

class GetCurrentSessionsResponse(_message.Message):
    __slots__ = ("session_keys", "success")
    SESSION_KEYS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    session_keys: _containers.RepeatedScalarFieldContainer[str]
    success: bool
    def __init__(self, session_keys: _Optional[_Iterable[str]] = ..., success: bool = ...) -> None: ...

class GetSessionInfoRequest(_message.Message):
    __slots__ = ("session_key",)
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    session_key: str
    def __init__(self, session_key: _Optional[str] = ...) -> None: ...

class GetSessionInfoResponse(_message.Message):
    __slots__ = ("data_source", "identifier", "type", "version", "associate_session_keys", "is_complete", "streams", "topic_partition_offsets", "main_offset", "essentials_offset", "details", "utc_offset", "success", "creation_time", "termination_time")
    class TopicPartitionOffsetsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class DetailsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_SESSION_KEYS_FIELD_NUMBER: _ClassVar[int]
    IS_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    STREAMS_FIELD_NUMBER: _ClassVar[int]
    TOPIC_PARTITION_OFFSETS_FIELD_NUMBER: _ClassVar[int]
    MAIN_OFFSET_FIELD_NUMBER: _ClassVar[int]
    ESSENTIALS_OFFSET_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    UTC_OFFSET_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIME_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_TIME_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    identifier: str
    type: str
    version: int
    associate_session_keys: _containers.RepeatedScalarFieldContainer[str]
    is_complete: bool
    streams: _containers.RepeatedScalarFieldContainer[str]
    topic_partition_offsets: _containers.ScalarMap[str, int]
    main_offset: int
    essentials_offset: int
    details: _containers.ScalarMap[str, str]
    utc_offset: _duration_pb2.Duration
    success: bool
    creation_time: _timestamp_pb2.Timestamp
    termination_time: _timestamp_pb2.Timestamp
    def __init__(self, data_source: _Optional[str] = ..., identifier: _Optional[str] = ..., type: _Optional[str] = ..., version: _Optional[int] = ..., associate_session_keys: _Optional[_Iterable[str]] = ..., is_complete: bool = ..., streams: _Optional[_Iterable[str]] = ..., topic_partition_offsets: _Optional[_Mapping[str, int]] = ..., main_offset: _Optional[int] = ..., essentials_offset: _Optional[int] = ..., details: _Optional[_Mapping[str, str]] = ..., utc_offset: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., success: bool = ..., creation_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., termination_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetSessionStartNotificationRequest(_message.Message):
    __slots__ = ("data_source",)
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    def __init__(self, data_source: _Optional[str] = ...) -> None: ...

class GetSessionStartNotificationResponse(_message.Message):
    __slots__ = ("session_key", "data_source")
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    session_key: str
    data_source: str
    def __init__(self, session_key: _Optional[str] = ..., data_source: _Optional[str] = ...) -> None: ...

class GetSessionStopNotificationRequest(_message.Message):
    __slots__ = ("data_source",)
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    def __init__(self, data_source: _Optional[str] = ...) -> None: ...

class GetSessionStopNotificationResponse(_message.Message):
    __slots__ = ("session_key", "data_source")
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    session_key: str
    data_source: str
    def __init__(self, session_key: _Optional[str] = ..., data_source: _Optional[str] = ...) -> None: ...

class UpdateSessionIdentifierRequest(_message.Message):
    __slots__ = ("session_key", "identifier")
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    session_key: str
    identifier: str
    def __init__(self, session_key: _Optional[str] = ..., identifier: _Optional[str] = ...) -> None: ...

class UpdateSessionIdentifierResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class AddAssociateSessionRequest(_message.Message):
    __slots__ = ("session_key", "associate_session_key")
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    session_key: str
    associate_session_key: str
    def __init__(self, session_key: _Optional[str] = ..., associate_session_key: _Optional[str] = ...) -> None: ...

class AddAssociateSessionResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class UpdateSessionDetailsRequest(_message.Message):
    __slots__ = ("session_key", "details")
    class DetailsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    session_key: str
    details: _containers.ScalarMap[str, str]
    def __init__(self, session_key: _Optional[str] = ..., details: _Optional[_Mapping[str, str]] = ...) -> None: ...

class UpdateSessionDetailsResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
