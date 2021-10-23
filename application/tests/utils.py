import inspect


class InvalidImplementationSignature(Exception):
    def __init__(
        self, reference: inspect.Signature, input: inspect.Signature, *args: object
    ):
        super().__init__(*args)
        self.message = f"Input signature {input} difers from reference {reference}"


def check_interface_implementation(interface_signature, reference_object, test_objects):
    for test_object in test_objects:
        for name, obj in inspect.getmembers(reference_object):
            if name.startswith("_"):
                continue
            interface_signature[name] = inspect.signature(obj)

        for name, obj in inspect.getmembers(test_object):
            if name.startswith("_"):
                continue

            if name in interface_signature:
                test_signature = interface_signature[name]
                if test_signature != inspect.signature(obj):
                    raise InvalidImplementationSignature(
                        reference=obj, input=interface_signature[name]
                    )
