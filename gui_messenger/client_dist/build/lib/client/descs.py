class Port:
    """Descriptor for port object"""

    def __init__(self):
        self._value = 7777
        print('init')

    def __get__(self, instance, instance_type):
        print('get')
        return self._value

    def __set__(self, instance, value):
        print('set')
        if not (1024 <= value < 65536):
            raise ValueError('Please, specify safe port (1024-65536)')
        self._value = value

