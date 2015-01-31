import dbus
import dbus.bus
import dbus.connection
import weakref


class DirectBusConnection(dbus.bus.BusConnection):
    '''
    dbus_bus_register() fails for direct address connections,
    so we avoid that by creating a connection directly
    '''
    def __new__(self, address):
        bus = dbus.connection.Connection(address)
        bus._bus_names = weakref.WeakValueDictionary()
        bus._signal_sender_matches = {}
        return bus


class UpstartSystem(object):
    def __init__(self, direct=False):
        if direct:
            self.__system = DirectBusConnection('unix:abstract=/com/ubuntu/upstart')
        else:
            self.__system = dbus.SystemBus()
        self.__o = self.__system.get_object(
                    'com.ubuntu.Upstart',
                    '/com/ubuntu/Upstart')

        self.__upstart_i = dbus.Interface(
                                self.__o,
                                'com.ubuntu.Upstart0_6')

        self.__property_i = dbus.Interface(
                                self.__o,
                                'org.freedesktop.DBus.Properties')

    def get_version(self):
        return self.__property_i.Get('com.ubuntu.Upstart0_6', 'version')

    def get_log_priority(self):
        return self.__property_i.Get('com.ubuntu.Upstart0_6', 'log_priority')

    def set_log_priority(self, priority_string):
        self.__property_i.Set(
            'com.ubuntu.Upstart0_6',
            'log_priority',
            priority_string)

    def get_all_jobs(self):
        return (j[j.rfind('/') + 1:] for j in self.__upstart_i.GetAllJobs())

    def emit(self, event_name, env={}, is_sync=True):
        env_list_ = [('%s=%s' % (str(k), str(v))) for (k,v) in env.iteritems()]
        self.__upstart_i.EmitEvent(event_name, env_list_, is_sync)

