class Client:
    def __init__(self, port, message_format, connection, topic=None ):
        self.port = port
        self.message_type = topic
        self.connection = connection
        self.message_format = message_format

    def to_string(self):
        return "{}, {}, {}".format(self.port, self.message_type, self.message_format)