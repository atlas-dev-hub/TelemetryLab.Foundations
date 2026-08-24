import datetime

from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DATA_TYPE_UNSPECIFIED: _ClassVar[DataType]
    DATA_TYPE_FLOAT64: _ClassVar[DataType]
    DATA_TYPE_FLOAT32: _ClassVar[DataType]
    DATA_TYPE_UINT32: _ClassVar[DataType]
    DATA_TYPE_SINT32: _ClassVar[DataType]
    DATA_TYPE_UINT16: _ClassVar[DataType]
    DATA_TYPE_SINT16: _ClassVar[DataType]
    DATA_TYPE_UINT8: _ClassVar[DataType]
    DATA_TYPE_SINT8: _ClassVar[DataType]
    DATA_TYPE_STRING: _ClassVar[DataType]

class EventPriority(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_PRIORITY_UNSPECIFIED: _ClassVar[EventPriority]
    EVENT_PRIORITY_CRITICAL: _ClassVar[EventPriority]
    EVENT_PRIORITY_HIGH: _ClassVar[EventPriority]
    EVENT_PRIORITY_MEDIUM: _ClassVar[EventPriority]
    EVENT_PRIORITY_LOW: _ClassVar[EventPriority]
    EVENT_PRIORITY_DEBUG: _ClassVar[EventPriority]

class FormulaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FORMULA_TYPE_UNSPECIFIED: _ClassVar[FormulaType]
    FORMULA_TYPE_FDL: _ClassVar[FormulaType]
    FORMULA_TYPE_CSHARP: _ClassVar[FormulaType]

class DataFormatType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DATA_FORMAT_TYPE_UNSPECIFIED: _ClassVar[DataFormatType]
    DATA_FORMAT_TYPE_PARAMETER: _ClassVar[DataFormatType]
    DATA_FORMAT_TYPE_EVENT: _ClassVar[DataFormatType]

class DataStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DATA_STATUS_UNSPECIFIED: _ClassVar[DataStatus]
    DATA_STATUS_VALID: _ClassVar[DataStatus]
    DATA_STATUS_MISSING: _ClassVar[DataStatus]
    DATA_STATUS_ERROR: _ClassVar[DataStatus]

class CanType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CAN_TYPE_UNSPECIFIED: _ClassVar[CanType]
    CAN_TYPE_TRANSMIT: _ClassVar[CanType]
    CAN_TYPE_RECEIVE: _ClassVar[CanType]

class SystemStatusType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SYSTEM_STATUS_TYPE_UNSPECIFIED: _ClassVar[SystemStatusType]
    SYSTEM_STATUS_TYPE_HEARTBEAT: _ClassVar[SystemStatusType]
    SYSTEM_STATUS_TYPE_STATUS: _ClassVar[SystemStatusType]
    SYSTEM_STATUS_TYPE_ERROR: _ClassVar[SystemStatusType]
    SYSTEM_STATUS_TYPE_WARNING: _ClassVar[SystemStatusType]
    SYSTEM_STATUS_TYPE_CONNECTION: _ClassVar[SystemStatusType]

class ErrorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_TYPE_UNSPECIFIED: _ClassVar[ErrorType]
    ERROR_TYPE_CURRENT: _ClassVar[ErrorType]
    ERROR_TYPE_LOGGED: _ClassVar[ErrorType]

class ErrorStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_STATUS_UNSPECIFIED: _ClassVar[ErrorStatus]
    ERROR_STATUS_SET: _ClassVar[ErrorStatus]
    ERROR_STATUS_CLEARED: _ClassVar[ErrorStatus]
DATA_TYPE_UNSPECIFIED: DataType
DATA_TYPE_FLOAT64: DataType
DATA_TYPE_FLOAT32: DataType
DATA_TYPE_UINT32: DataType
DATA_TYPE_SINT32: DataType
DATA_TYPE_UINT16: DataType
DATA_TYPE_SINT16: DataType
DATA_TYPE_UINT8: DataType
DATA_TYPE_SINT8: DataType
DATA_TYPE_STRING: DataType
EVENT_PRIORITY_UNSPECIFIED: EventPriority
EVENT_PRIORITY_CRITICAL: EventPriority
EVENT_PRIORITY_HIGH: EventPriority
EVENT_PRIORITY_MEDIUM: EventPriority
EVENT_PRIORITY_LOW: EventPriority
EVENT_PRIORITY_DEBUG: EventPriority
FORMULA_TYPE_UNSPECIFIED: FormulaType
FORMULA_TYPE_FDL: FormulaType
FORMULA_TYPE_CSHARP: FormulaType
DATA_FORMAT_TYPE_UNSPECIFIED: DataFormatType
DATA_FORMAT_TYPE_PARAMETER: DataFormatType
DATA_FORMAT_TYPE_EVENT: DataFormatType
DATA_STATUS_UNSPECIFIED: DataStatus
DATA_STATUS_VALID: DataStatus
DATA_STATUS_MISSING: DataStatus
DATA_STATUS_ERROR: DataStatus
CAN_TYPE_UNSPECIFIED: CanType
CAN_TYPE_TRANSMIT: CanType
CAN_TYPE_RECEIVE: CanType
SYSTEM_STATUS_TYPE_UNSPECIFIED: SystemStatusType
SYSTEM_STATUS_TYPE_HEARTBEAT: SystemStatusType
SYSTEM_STATUS_TYPE_STATUS: SystemStatusType
SYSTEM_STATUS_TYPE_ERROR: SystemStatusType
SYSTEM_STATUS_TYPE_WARNING: SystemStatusType
SYSTEM_STATUS_TYPE_CONNECTION: SystemStatusType
ERROR_TYPE_UNSPECIFIED: ErrorType
ERROR_TYPE_CURRENT: ErrorType
ERROR_TYPE_LOGGED: ErrorType
ERROR_STATUS_UNSPECIFIED: ErrorStatus
ERROR_STATUS_SET: ErrorStatus
ERROR_STATUS_CLEARED: ErrorStatus

class Packet(_message.Message):
    __slots__ = ("type", "session_key", "is_essential", "content", "id")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    IS_ESSENTIAL_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    type: str
    session_key: str
    is_essential: bool
    content: bytes
    id: int
    def __init__(self, type: _Optional[str] = ..., session_key: _Optional[str] = ..., is_essential: bool = ..., content: _Optional[bytes] = ..., id: _Optional[int] = ...) -> None: ...

class NewSessionPacket(_message.Message):
    __slots__ = ("data_source", "topic_partition_offsets", "utc_offset", "session_info", "creation_time")
    class TopicPartitionOffsetsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    TOPIC_PARTITION_OFFSETS_FIELD_NUMBER: _ClassVar[int]
    UTC_OFFSET_FIELD_NUMBER: _ClassVar[int]
    SESSION_INFO_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIME_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    topic_partition_offsets: _containers.ScalarMap[str, int]
    utc_offset: _duration_pb2.Duration
    session_info: SessionInfoPacket
    creation_time: _timestamp_pb2.Timestamp
    def __init__(self, data_source: _Optional[str] = ..., topic_partition_offsets: _Optional[_Mapping[str, int]] = ..., utc_offset: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., session_info: _Optional[_Union[SessionInfoPacket, _Mapping]] = ..., creation_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class EndOfSessionPacket(_message.Message):
    __slots__ = ("data_source", "topic_partition_offsets", "termination_time")
    class TopicPartitionOffsetsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    TOPIC_PARTITION_OFFSETS_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_TIME_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    topic_partition_offsets: _containers.ScalarMap[str, int]
    termination_time: _timestamp_pb2.Timestamp
    def __init__(self, data_source: _Optional[str] = ..., topic_partition_offsets: _Optional[_Mapping[str, int]] = ..., termination_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CoverageCursorInfoPacket(_message.Message):
    __slots__ = ("data_source", "coverage_cursor_time")
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    COVERAGE_CURSOR_TIME_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    coverage_cursor_time: int
    def __init__(self, data_source: _Optional[str] = ..., coverage_cursor_time: _Optional[int] = ...) -> None: ...

class SessionInfoPacket(_message.Message):
    __slots__ = ("data_source", "identifier", "type", "version", "associate_session_keys", "details", "utc_offset", "creation_time", "termination_time")
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
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    UTC_OFFSET_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIME_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_TIME_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    identifier: str
    type: str
    version: int
    associate_session_keys: _containers.RepeatedScalarFieldContainer[str]
    details: _containers.ScalarMap[str, str]
    utc_offset: _duration_pb2.Duration
    creation_time: _timestamp_pb2.Timestamp
    termination_time: _timestamp_pb2.Timestamp
    def __init__(self, data_source: _Optional[str] = ..., identifier: _Optional[str] = ..., type: _Optional[str] = ..., version: _Optional[int] = ..., associate_session_keys: _Optional[_Iterable[str]] = ..., details: _Optional[_Mapping[str, str]] = ..., utc_offset: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., creation_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., termination_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MetadataPacket(_message.Message):
    __slots__ = ("metadata",)
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    METADATA_FIELD_NUMBER: _ClassVar[int]
    metadata: _containers.MessageMap[str, _any_pb2.Any]
    def __init__(self, metadata: _Optional[_Mapping[str, _any_pb2.Any]] = ...) -> None: ...

class ConfigurationPacket(_message.Message):
    __slots__ = ("config_id", "parameter_definitions", "event_definitions", "group_definitions", "partial_packet", "packet_number", "total_packet_number")
    CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_DEFINITIONS_FIELD_NUMBER: _ClassVar[int]
    EVENT_DEFINITIONS_FIELD_NUMBER: _ClassVar[int]
    GROUP_DEFINITIONS_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_PACKET_FIELD_NUMBER: _ClassVar[int]
    PACKET_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PACKET_NUMBER_FIELD_NUMBER: _ClassVar[int]
    config_id: str
    parameter_definitions: _containers.RepeatedCompositeFieldContainer[ParameterDefinition]
    event_definitions: _containers.RepeatedCompositeFieldContainer[EventDefinition]
    group_definitions: _containers.RepeatedCompositeFieldContainer[GroupDefinition]
    partial_packet: bool
    packet_number: int
    total_packet_number: int
    def __init__(self, config_id: _Optional[str] = ..., parameter_definitions: _Optional[_Iterable[_Union[ParameterDefinition, _Mapping]]] = ..., event_definitions: _Optional[_Iterable[_Union[EventDefinition, _Mapping]]] = ..., group_definitions: _Optional[_Iterable[_Union[GroupDefinition, _Mapping]]] = ..., partial_packet: bool = ..., packet_number: _Optional[int] = ..., total_packet_number: _Optional[int] = ...) -> None: ...

class EventDefinition(_message.Message):
    __slots__ = ("identifier", "name", "definition_id", "application_name", "description", "priority", "groups", "data_types", "format_strings", "conversions", "units")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPES_FIELD_NUMBER: _ClassVar[int]
    FORMAT_STRINGS_FIELD_NUMBER: _ClassVar[int]
    CONVERSIONS_FIELD_NUMBER: _ClassVar[int]
    UNITS_FIELD_NUMBER: _ClassVar[int]
    identifier: str
    name: str
    definition_id: int
    application_name: str
    description: str
    priority: EventPriority
    groups: _containers.RepeatedScalarFieldContainer[str]
    data_types: _containers.RepeatedScalarFieldContainer[DataType]
    format_strings: _containers.RepeatedScalarFieldContainer[str]
    conversions: _containers.RepeatedCompositeFieldContainer[TextConversionDefinition]
    units: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, identifier: _Optional[str] = ..., name: _Optional[str] = ..., definition_id: _Optional[int] = ..., application_name: _Optional[str] = ..., description: _Optional[str] = ..., priority: _Optional[_Union[EventPriority, str]] = ..., groups: _Optional[_Iterable[str]] = ..., data_types: _Optional[_Iterable[_Union[DataType, str]]] = ..., format_strings: _Optional[_Iterable[str]] = ..., conversions: _Optional[_Iterable[_Union[TextConversionDefinition, _Mapping]]] = ..., units: _Optional[_Iterable[str]] = ...) -> None: ...

class ParameterDefinition(_message.Message):
    __slots__ = ("identifier", "name", "application_name", "description", "groups", "units", "data_type", "format_string", "min_value", "max_value", "warning_min_value", "warning_max_value", "frequencies", "includes_row_data", "includes_synchro_data", "conversion", "formula")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    UNITS_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    FORMAT_STRING_FIELD_NUMBER: _ClassVar[int]
    MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    WARNING_MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    WARNING_MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    FREQUENCIES_FIELD_NUMBER: _ClassVar[int]
    INCLUDES_ROW_DATA_FIELD_NUMBER: _ClassVar[int]
    INCLUDES_SYNCHRO_DATA_FIELD_NUMBER: _ClassVar[int]
    CONVERSION_FIELD_NUMBER: _ClassVar[int]
    FORMULA_FIELD_NUMBER: _ClassVar[int]
    identifier: str
    name: str
    application_name: str
    description: str
    groups: _containers.RepeatedScalarFieldContainer[str]
    units: str
    data_type: DataType
    format_string: str
    min_value: float
    max_value: float
    warning_min_value: float
    warning_max_value: float
    frequencies: _containers.RepeatedScalarFieldContainer[float]
    includes_row_data: bool
    includes_synchro_data: bool
    conversion: TextConversionDefinition
    formula: FormulaDefinition
    def __init__(self, identifier: _Optional[str] = ..., name: _Optional[str] = ..., application_name: _Optional[str] = ..., description: _Optional[str] = ..., groups: _Optional[_Iterable[str]] = ..., units: _Optional[str] = ..., data_type: _Optional[_Union[DataType, str]] = ..., format_string: _Optional[str] = ..., min_value: _Optional[float] = ..., max_value: _Optional[float] = ..., warning_min_value: _Optional[float] = ..., warning_max_value: _Optional[float] = ..., frequencies: _Optional[_Iterable[float]] = ..., includes_row_data: bool = ..., includes_synchro_data: bool = ..., conversion: _Optional[_Union[TextConversionDefinition, _Mapping]] = ..., formula: _Optional[_Union[FormulaDefinition, _Mapping]] = ...) -> None: ...

class TextConversionDefinition(_message.Message):
    __slots__ = ("conversion_identifier", "input_values", "string_values", "default")
    CONVERSION_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    INPUT_VALUES_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FIELD_NUMBER: _ClassVar[int]
    conversion_identifier: str
    input_values: _containers.RepeatedScalarFieldContainer[float]
    string_values: _containers.RepeatedScalarFieldContainer[str]
    default: str
    def __init__(self, conversion_identifier: _Optional[str] = ..., input_values: _Optional[_Iterable[float]] = ..., string_values: _Optional[_Iterable[str]] = ..., default: _Optional[str] = ...) -> None: ...

class FormulaDefinition(_message.Message):
    __slots__ = ("type", "formula")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FORMULA_FIELD_NUMBER: _ClassVar[int]
    type: FormulaType
    formula: str
    def __init__(self, type: _Optional[_Union[FormulaType, str]] = ..., formula: _Optional[str] = ...) -> None: ...

class GroupDefinition(_message.Message):
    __slots__ = ("identifier", "name", "application_name", "description", "groups")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    identifier: str
    name: str
    application_name: str
    description: str
    groups: _containers.RepeatedCompositeFieldContainer[GroupDefinition]
    def __init__(self, identifier: _Optional[str] = ..., name: _Optional[str] = ..., application_name: _Optional[str] = ..., description: _Optional[str] = ..., groups: _Optional[_Iterable[_Union[GroupDefinition, _Mapping]]] = ...) -> None: ...

class DataFormatConfigurationPacket(_message.Message):
    __slots__ = ("data_format_id", "data_formats")
    DATA_FORMAT_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FORMATS_FIELD_NUMBER: _ClassVar[int]
    data_format_id: str
    data_formats: _containers.RepeatedCompositeFieldContainer[DataFormatDefinitionPacket]
    def __init__(self, data_format_id: _Optional[str] = ..., data_formats: _Optional[_Iterable[_Union[DataFormatDefinitionPacket, _Mapping]]] = ...) -> None: ...

class ParameterList(_message.Message):
    __slots__ = ("parameter_identifiers",)
    PARAMETER_IDENTIFIERS_FIELD_NUMBER: _ClassVar[int]
    parameter_identifiers: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, parameter_identifiers: _Optional[_Iterable[str]] = ...) -> None: ...

class DataFormatDefinitionPacket(_message.Message):
    __slots__ = ("identifier", "type", "parameter_identifiers", "event_identifier")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_IDENTIFIERS_FIELD_NUMBER: _ClassVar[int]
    EVENT_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    identifier: int
    type: DataFormatType
    parameter_identifiers: ParameterList
    event_identifier: str
    def __init__(self, identifier: _Optional[int] = ..., type: _Optional[_Union[DataFormatType, str]] = ..., parameter_identifiers: _Optional[_Union[ParameterList, _Mapping]] = ..., event_identifier: _Optional[str] = ...) -> None: ...

class EventDataFormat(_message.Message):
    __slots__ = ("data_format_identifier", "event_identifier")
    DATA_FORMAT_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    EVENT_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    data_format_identifier: int
    event_identifier: str
    def __init__(self, data_format_identifier: _Optional[int] = ..., event_identifier: _Optional[str] = ...) -> None: ...

class EventPacket(_message.Message):
    __slots__ = ("data_format", "timestamp", "raw_values")
    DATA_FORMAT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RAW_VALUES_FIELD_NUMBER: _ClassVar[int]
    data_format: EventDataFormat
    timestamp: int
    raw_values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, data_format: _Optional[_Union[EventDataFormat, _Mapping]] = ..., timestamp: _Optional[int] = ..., raw_values: _Optional[_Iterable[float]] = ...) -> None: ...

class MarkerPacket(_message.Message):
    __slots__ = ("timestamp", "end_time", "label", "type", "description", "source", "value")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    end_time: int
    label: str
    type: str
    description: str
    source: str
    value: int
    def __init__(self, timestamp: _Optional[int] = ..., end_time: _Optional[int] = ..., label: _Optional[str] = ..., type: _Optional[str] = ..., description: _Optional[str] = ..., source: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...

class SampleDataFormat(_message.Message):
    __slots__ = ("data_format_identifier", "parameter_identifiers")
    DATA_FORMAT_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_IDENTIFIERS_FIELD_NUMBER: _ClassVar[int]
    data_format_identifier: int
    parameter_identifiers: ParameterList
    def __init__(self, data_format_identifier: _Optional[int] = ..., parameter_identifiers: _Optional[_Union[ParameterList, _Mapping]] = ...) -> None: ...

class SampleColumn(_message.Message):
    __slots__ = ("double_samples", "int32_samples", "bool_samples", "string_samples")
    DOUBLE_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    INT32_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    BOOL_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    STRING_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    double_samples: DoubleSampleList
    int32_samples: Int32SampleList
    bool_samples: BoolSampleList
    string_samples: StringSampleList
    def __init__(self, double_samples: _Optional[_Union[DoubleSampleList, _Mapping]] = ..., int32_samples: _Optional[_Union[Int32SampleList, _Mapping]] = ..., bool_samples: _Optional[_Union[BoolSampleList, _Mapping]] = ..., string_samples: _Optional[_Union[StringSampleList, _Mapping]] = ...) -> None: ...

class SampleRow(_message.Message):
    __slots__ = ("double_samples", "int32_samples", "bool_samples", "string_samples")
    DOUBLE_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    INT32_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    BOOL_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    STRING_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    double_samples: DoubleSampleList
    int32_samples: Int32SampleList
    bool_samples: BoolSampleList
    string_samples: StringSampleList
    def __init__(self, double_samples: _Optional[_Union[DoubleSampleList, _Mapping]] = ..., int32_samples: _Optional[_Union[Int32SampleList, _Mapping]] = ..., bool_samples: _Optional[_Union[BoolSampleList, _Mapping]] = ..., string_samples: _Optional[_Union[StringSampleList, _Mapping]] = ...) -> None: ...

class DoubleSampleList(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[DoubleSample]
    def __init__(self, samples: _Optional[_Iterable[_Union[DoubleSample, _Mapping]]] = ...) -> None: ...

class Int32SampleList(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[Int32Sample]
    def __init__(self, samples: _Optional[_Iterable[_Union[Int32Sample, _Mapping]]] = ...) -> None: ...

class BoolSampleList(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[BoolSample]
    def __init__(self, samples: _Optional[_Iterable[_Union[BoolSample, _Mapping]]] = ...) -> None: ...

class StringSampleList(_message.Message):
    __slots__ = ("samples",)
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[StringSample]
    def __init__(self, samples: _Optional[_Iterable[_Union[StringSample, _Mapping]]] = ...) -> None: ...

class DoubleSample(_message.Message):
    __slots__ = ("value", "status")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    value: float
    status: DataStatus
    def __init__(self, value: _Optional[float] = ..., status: _Optional[_Union[DataStatus, str]] = ...) -> None: ...

class Int32Sample(_message.Message):
    __slots__ = ("value", "status")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    value: int
    status: DataStatus
    def __init__(self, value: _Optional[int] = ..., status: _Optional[_Union[DataStatus, str]] = ...) -> None: ...

class BoolSample(_message.Message):
    __slots__ = ("value", "status")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    value: bool
    status: DataStatus
    def __init__(self, value: bool = ..., status: _Optional[_Union[DataStatus, str]] = ...) -> None: ...

class StringSample(_message.Message):
    __slots__ = ("value", "status")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    value: str
    status: DataStatus
    def __init__(self, value: _Optional[str] = ..., status: _Optional[_Union[DataStatus, str]] = ...) -> None: ...

class RowDataPacket(_message.Message):
    __slots__ = ("data_format", "timestamps", "rows")
    DATA_FORMAT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    data_format: SampleDataFormat
    timestamps: _containers.RepeatedScalarFieldContainer[int]
    rows: _containers.RepeatedCompositeFieldContainer[SampleRow]
    def __init__(self, data_format: _Optional[_Union[SampleDataFormat, _Mapping]] = ..., timestamps: _Optional[_Iterable[int]] = ..., rows: _Optional[_Iterable[_Union[SampleRow, _Mapping]]] = ...) -> None: ...

class PeriodicDataPacket(_message.Message):
    __slots__ = ("data_format", "start_time", "interval", "columns")
    DATA_FORMAT_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    data_format: SampleDataFormat
    start_time: int
    interval: int
    columns: _containers.RepeatedCompositeFieldContainer[SampleColumn]
    def __init__(self, data_format: _Optional[_Union[SampleDataFormat, _Mapping]] = ..., start_time: _Optional[int] = ..., interval: _Optional[int] = ..., columns: _Optional[_Iterable[_Union[SampleColumn, _Mapping]]] = ...) -> None: ...

class SynchroDataPacket(_message.Message):
    __slots__ = ("data_format", "start_time", "intervals", "columns")
    DATA_FORMAT_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    INTERVALS_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    data_format: SampleDataFormat
    start_time: int
    intervals: _containers.RepeatedScalarFieldContainer[int]
    columns: _containers.RepeatedCompositeFieldContainer[SampleColumn]
    def __init__(self, data_format: _Optional[_Union[SampleDataFormat, _Mapping]] = ..., start_time: _Optional[int] = ..., intervals: _Optional[_Iterable[int]] = ..., columns: _Optional[_Iterable[_Union[SampleColumn, _Mapping]]] = ...) -> None: ...

class RawCANDataPacket(_message.Message):
    __slots__ = ("timestamp", "bus", "can_id", "payload", "type")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    BUS_FIELD_NUMBER: _ClassVar[int]
    CAN_ID_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    bus: int
    can_id: int
    payload: bytes
    type: CanType
    def __init__(self, timestamp: _Optional[int] = ..., bus: _Optional[int] = ..., can_id: _Optional[int] = ..., payload: _Optional[bytes] = ..., type: _Optional[_Union[CanType, str]] = ...) -> None: ...

class ValueArray(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, values: _Optional[_Iterable[float]] = ...) -> None: ...

class AxisDataPacket(_message.Message):
    __slots__ = ("axis_identifier", "timestamp", "values")
    AXIS_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    axis_identifier: str
    timestamp: int
    values: ValueArray
    def __init__(self, axis_identifier: _Optional[str] = ..., timestamp: _Optional[int] = ..., values: _Optional[_Union[ValueArray, _Mapping]] = ...) -> None: ...

class MapDataPacket(_message.Message):
    __slots__ = ("map_identifier", "timestamp", "x_axis_identifier", "x_index_identifier", "y_axis_identifier", "y_index_identifier", "values")
    MAP_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    X_AXIS_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    X_INDEX_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    Y_AXIS_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    Y_INDEX_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    map_identifier: str
    timestamp: int
    x_axis_identifier: str
    x_index_identifier: str
    y_axis_identifier: str
    y_index_identifier: str
    values: _containers.RepeatedCompositeFieldContainer[ValueArray]
    def __init__(self, map_identifier: _Optional[str] = ..., timestamp: _Optional[int] = ..., x_axis_identifier: _Optional[str] = ..., x_index_identifier: _Optional[str] = ..., y_axis_identifier: _Optional[str] = ..., y_index_identifier: _Optional[str] = ..., values: _Optional[_Iterable[_Union[ValueArray, _Mapping]]] = ...) -> None: ...

class SystemStatusMessage(_message.Message):
    __slots__ = ("service", "data_source", "type")
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    service: str
    data_source: str
    type: SystemStatusType
    def __init__(self, service: _Optional[str] = ..., data_source: _Optional[str] = ..., type: _Optional[_Union[SystemStatusType, str]] = ...) -> None: ...

class ErrorPacket(_message.Message):
    __slots__ = ("error_identifier", "timestamp", "application_name", "group", "name", "description", "type", "status")
    ERROR_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    APPLICATION_NAME_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    error_identifier: str
    timestamp: int
    application_name: str
    group: str
    name: str
    description: str
    type: ErrorType
    status: ErrorStatus
    def __init__(self, error_identifier: _Optional[str] = ..., timestamp: _Optional[int] = ..., application_name: _Optional[str] = ..., group: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[ErrorType, str]] = ..., status: _Optional[_Union[ErrorStatus, str]] = ...) -> None: ...

class StreamStartedPacket(_message.Message):
    __slots__ = ("data_source", "session_key", "stream_name", "start_time")
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    STREAM_NAME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    session_key: str
    stream_name: str
    start_time: _timestamp_pb2.Timestamp
    def __init__(self, data_source: _Optional[str] = ..., session_key: _Optional[str] = ..., stream_name: _Optional[str] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class StreamStoppedPacket(_message.Message):
    __slots__ = ("data_source", "session_key", "stream_name", "stop_time")
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    SESSION_KEY_FIELD_NUMBER: _ClassVar[int]
    STREAM_NAME_FIELD_NUMBER: _ClassVar[int]
    STOP_TIME_FIELD_NUMBER: _ClassVar[int]
    data_source: str
    session_key: str
    stream_name: str
    stop_time: _timestamp_pb2.Timestamp
    def __init__(self, data_source: _Optional[str] = ..., session_key: _Optional[str] = ..., stream_name: _Optional[str] = ..., stop_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
