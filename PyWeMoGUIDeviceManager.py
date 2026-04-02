import logging
import threading
from queue import Queue
import pywemo

class PyWeMoGUIDeviceManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_devices = []

    def discover_devices(self, queue: Queue):
        '''
        This function will discover devices on the local network, using a thread to not block the caller.

        To recieve data, **you must check a passed queue** for new data. Otherwise, this function will appear to do nothing.

        :param queue: Pass a fresh Queue object, it will have the pywemo devices array put into it once discovery is complete
        :type queue: Queue
        '''
        def _device_discovery(queue: Queue): #called in discover but is not discover itself
            self.logger.debug("Device discovery thread started, now discovering devices")
            self.current_devices = pywemo.discover_devices()
            queue.put(self.current_devices)
        self.logger.debug("Clearing device list before running discovery to avoid stale objects")
        self.current_devices.clear() # clear devices to avoid stale objects

        scanThread = threading.Thread(target=_device_discovery, args=(queue,)) #setup thread
        scanThread.daemon=True
        scanThread.start() # start actual discovery in thread

    #def list_devices(self):
    #    #return [device.name for device in self.current_devices]  #### this was never used
    #    pass
    
    def sort_list_by_name(self):
        self.current_devices.sort(key=lambda device: device.name)

    def get_device_by_name(self, name):
        '''
        Returns the device with the specified name
        
        :param index: The name of the device in the table to return
        '''
        for device in self.current_devices:
            if device.name == name:
                return device
        return None
    
    def get_device_by_ip(self, ip):
        '''
        Returns the device with the specified IP
        
        :param index: The IP of the device in the table to return
        '''
        for device in self.current_devices:
            if device.host == ip:
                return device
        return None
    
    def get_device_by_array_index(self, index: int): # Probably more performant than by name or ip
        '''
        Returns the device with the specified index
        
        :param index: The index of the device in the table to return
        '''
        if 0 <= index < len(self.current_devices):
            return self.current_devices[index]
        return None