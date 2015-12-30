# -*- coding: utf-8 -*-


def load_transport(module_path, class_name):
    _module = __import__(module_path, globals(), locals(), class_name, -1)
    return getattr(_module, class_name)


def create_transport(beaver_config, logger):
    """Creates and returns a transport object"""
    transport_str = beaver_config.get('transport')
    # allow simple names like 'redis' to load a beaver built-in transport
    if '.' not in transport_str:
        # Try import the new modular transport package
        try:
            module_path = 'beaver_{0}'.format(transport_str.lower())
            class_name = 'Transport'
            transport_class = load_transport(module_path, class_name)
        # Default back to built-in version and throw a deprecation warning
        except ImportError:
            logger.warn(
                ("You are using a deprecated version of the {0} transport ",
                 "library which will soon be removed. Upgrade by running ",
                 "'pip install beaver_{0}'".format(
                     transport_str.lower())))
            module_path = 'beaver.transports.{0}_transport'.format(
                transport_str.lower())
            class_name = '{0}Transport'.format(
                transport_str.title())
            transport_class = load_transport(module_path, class_name)
    else:
        # allow dotted path names to load a custom transport class
        try:
            module_path, class_name = transport_str.rsplit('.', 1)
        except ValueError:
            raise Exception(
                'Invalid transport {0}'.format(
                    beaver_config.get('transport')))

        transport_class = load_transport(module_path, class_name)

    transport = transport_class(beaver_config=beaver_config, logger=logger)

    return transport
