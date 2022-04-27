import dis


class ClientVerifier(type):
    """Metaclass for verifying if client is correct"""
    def __init__(cls, clsname, bases, clsdict):

        presence_get_message = False
        presence_send_message = False

        for func in clsdict.keys():
            ret = dis.get_instructions(clsdict[func])

            for i in ret:
                if i.opname == 'LOAD_GLOBAL':
                    if i.argval in ('accept', 'listen', 'socket'):
                        raise TypeError('You can\'t use accept/listen/socket in Client!')
                    if i.argval == 'get_message':
                        presence_get_message = True
                    elif i.argval == 'send_message':
                        presence_send_message = True
        if not any((presence_send_message, presence_get_message)):
            raise TypeError('Client has no get_message and send_message methods!')

        super().__init__(clsname, bases, clsdict)


class ServerVerifier(type):
    """Metaclass for verifying if server is correct"""
    def __init__(cls, clsname, bases, clsdict):

        methods_1 = []
        methods_2 = []
        attrs = []

        for func in clsdict.keys():
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError as e:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods_1:
                            methods_1.append(i.argval)
                    elif i.opname == 'LOAD_METHOD':
                        if i.argval not in methods_2:
                            methods_2.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)

        print(methods_1)
        print(methods_2)
        print(attrs)

        all_methods = []
        all_methods.extend(methods_1)
        all_methods.extend(methods_2)

        if 'connect' in all_methods:
            raise TypeError('You can\'t use connect in server methods')
        if not ('SOCK_STREAM' in attrs or 'SOCK_STREAM' in all_methods and 'AF_INET' in attrs or 'AF_INET' in all_methods):
            raise TypeError('Incorrect initialization of socket. Use SOCK_STREAM and AF_INET')

        super().__init__(clsname, bases, clsdict)
