message types:

- handshake : fields : port, message_format (json or xml), message_type (subscription topic)

- posting :  fields : message_type (subscription topic), message (text itself)

- greeting : fields : text, used when the server acknowledges a handshake

{
    name : handshake,
    message_format: xml,
    port : 777,
    message_type: weather
}

{
    name : posting,
    message_type : weather,
    message: 21 C
}

{
    name : greeting,
    text : Welcome
}