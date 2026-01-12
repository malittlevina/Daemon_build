# devices/adapters/usb_adapter.py
"""
USB Adapter
===========
Handles USB device detection, hotplug monitoring, and device information.

Supports:
- USB device enumeration
- Hotplug event monitoring
- Device class identification
- Serial device communication

Dependencies:
- pyudev: For Linux USB device monitoring
- pyusb: For cross-platform USB access
- pyserial: For serial device communication
"""

import threading
import time
import subprocess
from typing import Dict, List, Optional, Callable, Any
from .base_adapter import BaseProtocolAdapter, AdapterState

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from devices.device_registry import (
    Device, DeviceProtocol, DeviceState, DeviceCapability, DeviceMetadata
)


class USBAdapter(BaseProtocolAdapter):
    """
    USB adapter for device detection and monitoring.
    Supports hotplug events and device enumeration.
    """
    
    # USB device class codes and their capabilities
    USB_CLASSES = {
        0x00: ('Composite', []),
        0x01: ('Audio', [DeviceCapability.SPEAKER, DeviceCapability.MICROPHONE]),
        0x02: ('Communications', [DeviceCapability.NETWORK_BRIDGE]),
        0x03: ('HID', []),
        0x05: ('Physical', []),
        0x06: ('Image', [DeviceCapability.CAMERA]),
        0x07: ('Printer', []),
        0x08: ('Mass Storage', [DeviceCapability.STORAGE]),
        0x09: ('Hub', [DeviceCapability.NETWORK_BRIDGE]),
        0x0A: ('CDC-Data', []),
        0x0B: ('Smart Card', []),
        0x0D: ('Content Security', []),
        0x0E: ('Video', [DeviceCapability.CAMERA]),
        0x0F: ('Personal Healthcare', [DeviceCapability.SENSOR_ACCELEROMETER]),
        0x10: ('Audio/Video', [DeviceCapability.CAMERA, DeviceCapability.SPEAKER]),
        0xDC: ('Diagnostic', []),
        0xE0: ('Wireless', [DeviceCapability.NETWORK_BRIDGE]),
        0xEF: ('Miscellaneous', []),
        0xFE: ('Application Specific', []),
        0xFF: ('Vendor Specific', []),
    }
    
    # Known USB vendor IDs
    KNOWN_VENDORS = {
        0x05AC: 'Apple',
        0x0BDA: 'Realtek',
        0x8087: 'Intel',
        0x046D: 'Logitech',
        0x0781: 'SanDisk',
        0x054C: 'Sony',
        0x04E8: 'Samsung',
        0x0BB4: 'HTC',
        0x18D1: 'Google',
        0x2833: 'Oculus',
        0x045E: 'Microsoft',
        0x1532: 'Razer',
        0x1038: 'SteelSeries',
        0x1B1C: 'Corsair',
        0x2109: 'VIA Labs',
        0x0451: 'Texas Instruments',
        0x1A86: 'QinHeng Electronics',
        0x10C4: 'Silicon Labs',
        0x0403: 'FTDI',
        0x067B: 'Prolific',
        0x2341: 'Arduino',
        0x1D50: 'OpenMoko',
        0x239A: 'Adafruit',
        0x2E8A: 'Raspberry Pi',
    }
    
    def __init__(self):
        super().__init__("USBAdapter")
        self._pyudev_available = False
        self._pyusb_available = False
        self._pyserial_available = False
        self._monitor = None
        self._observer = None
        self._scan_active = False
        self._known_devices: Dict[str, Device] = {}
        
    def initialize(self) -> bool:
        """Initialize USB adapter and check for available libraries."""
        self.state = AdapterState.INITIALIZING
        print(f"[{self.name}] Initializing...")
        
        # Try to import pyudev (Linux)
        try:
            import pyudev
            self._pyudev_available = True
            print(f"[{self.name}] pyudev support available (Linux USB monitoring)")
        except ImportError:
            print(f"[{self.name}] pyudev not installed (Linux only).")
            print(f"[{self.name}] Install with: pip install pyudev")
        
        # Try to import pyusb
        try:
            import usb.core
            import usb.util
            self._pyusb_available = True
            print(f"[{self.name}] pyusb support available (cross-platform USB)")
        except ImportError:
            print(f"[{self.name}] pyusb not installed.")
            print(f"[{self.name}] Install with: pip install pyusb")
        except Exception as e:
            print(f"[{self.name}] pyusb available but: {e}")
            self._pyusb_available = True  # Still might work
        
        # Try to import pyserial
        try:
            import serial
            import serial.tools.list_ports
            self._pyserial_available = True
            print(f"[{self.name}] pyserial support available (serial ports)")
        except ImportError:
            print(f"[{self.name}] pyserial not installed.")
            print(f"[{self.name}] Install with: pip install pyserial")
        
        # Also try lsusb as fallback
        self._lsusb_available = self._check_lsusb()
        if self._lsusb_available:
            print(f"[{self.name}] lsusb fallback available")
        
        self._is_available = (
            self._pyudev_available or 
            self._pyusb_available or 
            self._pyserial_available or
            self._lsusb_available
        )
        
        if self._is_available:
            self.state = AdapterState.READY
            print(f"[{self.name}] Initialized successfully.")
        else:
            self.state = AdapterState.ERROR
            self._report_error("No USB libraries available")
            
        return self._is_available
    
    def _check_lsusb(self) -> bool:
        """Check if lsusb is available."""
        try:
            result = subprocess.run(['lsusb'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _enumerate_pyusb(self, callback: Callable):
        """Enumerate USB devices using pyusb."""
        try:
            import usb.core
            import usb.util
            
            print(f"[{self.name}] Enumerating USB devices with pyusb...")
            
            devices = usb.core.find(find_all=True)
            
            for dev in devices:
                if not self._scan_active:
                    break
                
                try:
                    device = self._pyusb_to_device(dev)
                    callback(device)
                except Exception as e:
                    # Some devices can't be accessed
                    pass
            
        except Exception as e:
            self._report_error(f"pyusb enumeration failed: {e}")
    
    def _pyusb_to_device(self, usb_dev) -> Device:
        """Convert pyusb device to Device."""
        import usb.core
        import usb.util
        
        device_id = f"usb_{usb_dev.bus}_{usb_dev.address}_{usb_dev.idVendor:04x}_{usb_dev.idProduct:04x}"
        
        # Get device class info
        device_class = usb_dev.bDeviceClass
        class_name, capabilities = self.USB_CLASSES.get(device_class, ('Unknown', []))
        
        # If device class is 0, check interface class
        if device_class == 0:
            try:
                cfg = usb_dev.get_active_configuration()
                if cfg:
                    for intf in cfg:
                        intf_class = intf.bInterfaceClass
                        if intf_class in self.USB_CLASSES:
                            class_name, capabilities = self.USB_CLASSES[intf_class]
                            break
            except Exception:
                pass
        
        # Get manufacturer and product strings
        manufacturer = None
        product = None
        serial = None
        
        try:
            if usb_dev.iManufacturer:
                manufacturer = usb.util.get_string(usb_dev, usb_dev.iManufacturer)
            if usb_dev.iProduct:
                product = usb.util.get_string(usb_dev, usb_dev.iProduct)
            if usb_dev.iSerialNumber:
                serial = usb.util.get_string(usb_dev, usb_dev.iSerialNumber)
        except Exception:
            # Permission denied or device busy
            manufacturer = self.KNOWN_VENDORS.get(usb_dev.idVendor)
        
        # Use known vendor as fallback
        if not manufacturer:
            manufacturer = self.KNOWN_VENDORS.get(usb_dev.idVendor)
        
        metadata = DeviceMetadata(
            manufacturer=manufacturer,
            model=product,
            serial_number=serial,
            last_seen=time.time(),
            custom_data={
                'vendor_id': f"0x{usb_dev.idVendor:04X}",
                'product_id': f"0x{usb_dev.idProduct:04X}",
                'bus': usb_dev.bus,
                'address': usb_dev.address,
                'device_class': class_name,
                'speed': self._get_usb_speed(usb_dev),
            }
        )
        
        name = product or f"{manufacturer or 'USB'} Device"
        
        return Device(
            id=device_id,
            name=name,
            protocol=DeviceProtocol.USB,
            state=DeviceState.CONNECTED,  # USB devices are always "connected" when present
            address=f"{usb_dev.bus}:{usb_dev.address}",
            capabilities=list(capabilities),
            metadata=metadata,
            services={'usb': {
                'vendor_id': usb_dev.idVendor,
                'product_id': usb_dev.idProduct,
                'class': device_class
            }}
        )
    
    def _get_usb_speed(self, usb_dev) -> str:
        """Get USB device speed."""
        try:
            speed = usb_dev.speed
            speeds = {
                0: 'Unknown',
                1: 'Low Speed (1.5 Mbps)',
                2: 'Full Speed (12 Mbps)',
                3: 'High Speed (480 Mbps)',
                4: 'Super Speed (5 Gbps)',
                5: 'Super Speed+ (10 Gbps)',
            }
            return speeds.get(speed, f'Speed {speed}')
        except Exception:
            return 'Unknown'
    
    def _enumerate_serial(self, callback: Callable):
        """Enumerate serial ports using pyserial."""
        try:
            import serial.tools.list_ports
            
            print(f"[{self.name}] Enumerating serial ports...")
            
            ports = serial.tools.list_ports.comports()
            
            for port in ports:
                if not self._scan_active:
                    break
                
                device = self._serial_to_device(port)
                callback(device)
            
            print(f"[{self.name}] Found {len(ports)} serial ports.")
            
        except Exception as e:
            self._report_error(f"Serial enumeration failed: {e}")
    
    def _serial_to_device(self, port) -> Device:
        """Convert serial port to Device."""
        device_id = f"serial_{port.device.replace('/', '_')}"
        
        # Determine capabilities
        capabilities = []
        if 'Arduino' in (port.manufacturer or '') or 'Arduino' in (port.description or ''):
            capabilities.append(DeviceCapability.COMPUTE)
        if 'GPS' in (port.description or '').upper():
            capabilities.append(DeviceCapability.GPS)
        
        metadata = DeviceMetadata(
            manufacturer=port.manufacturer,
            model=port.product,
            serial_number=port.serial_number,
            last_seen=time.time(),
            custom_data={
                'device': port.device,
                'description': port.description,
                'hwid': port.hwid,
                'vid': f"0x{port.vid:04X}" if port.vid else None,
                'pid': f"0x{port.pid:04X}" if port.pid else None,
                'location': port.location,
                'interface': port.interface
            }
        )
        
        return Device(
            id=device_id,
            name=port.description or port.device,
            protocol=DeviceProtocol.USB,
            state=DeviceState.CONNECTED,
            address=port.device,
            capabilities=capabilities,
            metadata=metadata,
            services={'serial': {
                'port': port.device,
                'vid': port.vid,
                'pid': port.pid
            }}
        )
    
    def _enumerate_lsusb(self, callback: Callable):
        """Enumerate USB devices using lsusb command."""
        try:
            result = subprocess.run(
                ['lsusb', '-v'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # Try without -v
                result = subprocess.run(
                    ['lsusb'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if result.returncode == 0:
                devices = self._parse_lsusb(result.stdout)
                for device in devices:
                    if not self._scan_active:
                        break
                    callback(device)
            
        except Exception as e:
            self._report_error(f"lsusb failed: {e}")
    
    def _parse_lsusb(self, output: str) -> List[Device]:
        """Parse lsusb output into Device objects."""
        import re
        
        devices = []
        
        # Parse basic lsusb format: Bus 001 Device 002: ID 1234:5678 Description
        pattern = r'Bus (\d+) Device (\d+): ID ([0-9a-fA-F]{4}):([0-9a-fA-F]{4})\s*(.*)'
        
        for line in output.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                bus, addr, vid, pid, desc = match.groups()
                
                vid_int = int(vid, 16)
                pid_int = int(pid, 16)
                
                device_id = f"usb_{bus}_{addr}_{vid}_{pid}"
                
                manufacturer = self.KNOWN_VENDORS.get(vid_int)
                
                metadata = DeviceMetadata(
                    manufacturer=manufacturer,
                    last_seen=time.time(),
                    custom_data={
                        'vendor_id': f"0x{vid.upper()}",
                        'product_id': f"0x{pid.upper()}",
                        'bus': int(bus),
                        'address': int(addr),
                    }
                )
                
                devices.append(Device(
                    id=device_id,
                    name=desc.strip() or f"USB Device {vid}:{pid}",
                    protocol=DeviceProtocol.USB,
                    state=DeviceState.CONNECTED,
                    address=f"{bus}:{addr}",
                    capabilities=[],
                    metadata=metadata,
                    services={'usb': {'vendor_id': vid_int, 'product_id': pid_int}}
                ))
        
        return devices
    
    def _start_hotplug_monitor(self, callback: Callable):
        """Start monitoring for USB hotplug events using pyudev."""
        try:
            import pyudev
            
            context = pyudev.Context()
            self._monitor = pyudev.Monitor.from_netlink(context)
            self._monitor.filter_by(subsystem='usb')
            
            def handle_event(action, device):
                if not self._scan_active:
                    return
                
                if action in ('add', 'bind'):
                    # New device connected
                    try:
                        dev = self._pyudev_to_device(device)
                        if dev:
                            callback(dev)
                    except Exception as e:
                        pass
            
            self._observer = pyudev.MonitorObserver(
                self._monitor,
                lambda action, device: handle_event(action, device)
            )
            self._observer.start()
            print(f"[{self.name}] USB hotplug monitoring started.")
            
        except Exception as e:
            print(f"[{self.name}] Hotplug monitoring failed: {e}")
    
    def _pyudev_to_device(self, udev) -> Optional[Device]:
        """Convert pyudev device to Device."""
        try:
            # Get vendor and product IDs
            vid = udev.get('ID_VENDOR_ID')
            pid = udev.get('ID_MODEL_ID')
            
            if not vid or not pid:
                return None
            
            vid_int = int(vid, 16)
            pid_int = int(pid, 16)
            
            device_id = f"usb_{udev.get('BUSNUM', '0')}_{udev.get('DEVNUM', '0')}_{vid}_{pid}"
            
            manufacturer = udev.get('ID_VENDOR') or self.KNOWN_VENDORS.get(vid_int)
            product = udev.get('ID_MODEL')
            serial = udev.get('ID_SERIAL_SHORT')
            
            metadata = DeviceMetadata(
                manufacturer=manufacturer,
                model=product,
                serial_number=serial,
                last_seen=time.time(),
                custom_data={
                    'vendor_id': f"0x{vid.upper()}",
                    'product_id': f"0x{pid.upper()}",
                    'devpath': udev.device_path,
                    'subsystem': udev.subsystem,
                }
            )
            
            return Device(
                id=device_id,
                name=product or f"{manufacturer or 'USB'} Device",
                protocol=DeviceProtocol.USB,
                state=DeviceState.CONNECTED,
                address=udev.device_path,
                capabilities=[],
                metadata=metadata,
                services={'usb': {'vendor_id': vid_int, 'product_id': pid_int}}
            )
            
        except Exception as e:
            return None
    
    def start_discovery(self, callback: Callable, duration: float = 5.0) -> bool:
        """Start USB device discovery and monitoring."""
        if not self._is_available:
            self._report_error("USB discovery not available")
            return False
        
        if self._scan_active:
            print(f"[{self.name}] Scan already in progress.")
            return False
        
        self._scan_active = True
        self.state = AdapterState.SCANNING
        
        def scan_thread():
            try:
                # Enumerate existing devices
                if self._pyusb_available:
                    self._enumerate_pyusb(callback)
                elif self._lsusb_available:
                    self._enumerate_lsusb(callback)
                
                # Enumerate serial ports
                if self._pyserial_available:
                    self._enumerate_serial(callback)
                
                # Start hotplug monitoring if available
                if self._pyudev_available:
                    self._start_hotplug_monitor(callback)
                    # Keep running for duration
                    time.sleep(duration)
                
            except Exception as e:
                self._report_error(f"Discovery error: {e}")
            finally:
                self._scan_active = False
                self.state = AdapterState.READY
        
        self._scan_thread = threading.Thread(target=scan_thread, daemon=True)
        self._scan_thread.start()
        
        return True
    
    def stop_discovery(self):
        """Stop USB discovery and monitoring."""
        self._scan_active = False
        
        if self._observer:
            try:
                self._observer.stop()
            except Exception:
                pass
            self._observer = None
        
        if self._scan_thread and self._scan_thread.is_alive():
            self._scan_thread.join(timeout=2.0)
        
        self.state = AdapterState.READY
        print(f"[{self.name}] Discovery stopped.")
    
    def connect(self, device_id: str) -> bool:
        """Connect to a USB device (claim interface)."""
        print(f"[{self.name}] USB devices are connected by default when plugged in.")
        return True
    
    def disconnect(self, device_id: str) -> bool:
        """Disconnect from a USB device."""
        return True
    
    def send_data(self, device_id: str, data: bytes) -> bool:
        """Send data to a USB device (for serial devices)."""
        if not self._pyserial_available:
            self._report_error("pyserial required for data transfer")
            return False
        
        # Extract serial port from device_id
        if not device_id.startswith('serial_'):
            self._report_error("Only serial devices support direct data transfer")
            return False
        
        try:
            import serial
            
            port = device_id.replace('serial_', '').replace('_', '/')
            with serial.Serial(port, 9600, timeout=1) as ser:
                ser.write(data)
            return True
            
        except Exception as e:
            self._report_error(f"Serial write failed: {e}")
            return False
    
    def receive_data(self, device_id: str, timeout: float = 5.0) -> Optional[bytes]:
        """Receive data from a USB device (for serial devices)."""
        if not self._pyserial_available:
            return None
        
        if not device_id.startswith('serial_'):
            return None
        
        try:
            import serial
            
            port = device_id.replace('serial_', '').replace('_', '/')
            with serial.Serial(port, 9600, timeout=timeout) as ser:
                return ser.read(1024)
            
        except Exception as e:
            self._report_error(f"Serial read failed: {e}")
            return None
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed USB device information."""
        # Re-enumerate to find the device
        if self._pyusb_available:
            try:
                import usb.core
                
                # Parse device_id to get vendor/product
                parts = device_id.split('_')
                if len(parts) >= 4:
                    vid = int(parts[-2], 16)
                    pid = int(parts[-1], 16)
                    
                    dev = usb.core.find(idVendor=vid, idProduct=pid)
                    if dev:
                        return self._pyusb_to_device(dev).to_dict()
            except Exception:
                pass
        
        return None
    
    def shutdown(self):
        """Shutdown the USB adapter."""
        self.stop_discovery()
        super().shutdown()
