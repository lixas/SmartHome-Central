# https://stackoverflow.com/a/28479007

class Observer():
    _observers = []

    def __init__(self):
        self._observers.append(self)
        self._observed_events = []

    def observe(self, event_name, callback_fn):
        self._observed_events.append({'event_name': event_name, 'callback_fn': callback_fn})

    def forget(self, event_name):
        for dict_item in self._observed_events:
            for key, val in dict_item.items():
                if val == event_name:
                    self._observed_events.remove(dict_item)


class Event():
    def __init__(self, event_name, *callback_args):
        for observer in Observer._observers:
            for observable in observer._observed_events:
                if observable['event_name'] == event_name:
                    observable['callback_fn'](*callback_args)


# Example:
'''
class Room(Observer):
    def __init__(self):
        print("Room is ready.")
        Observer.__init__(self)  # DON'T FORGET THIS

    def someone_arrived(self, who):
        print("{} has arrived!".format(who))


# Observe for specific event
room = Room()
room.observe('someone arrived', room.someone_arrived)

# Fire some events
Event('someone left', 'John')
Event('someone arrived', 'Lenard')  # will output "Lenard has arrived!"
Event('someone Farted', 'Lenard')

# Remove known event
room.forget('someone arrived')

# no events based on 'someone arrived' will be fired
'''
