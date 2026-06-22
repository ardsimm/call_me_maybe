from schema import Schema


class SchemaFactory:

    __schema_instance: Schema

    @staticmethod
    def get_instance() -> Schema:
        raise NotImplementedError(
            "Method get_instance of SchemaFactory"
            + " not yet implemented"
        )
