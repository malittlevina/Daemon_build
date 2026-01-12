# devices/adapters/nfc_adapter.py
"""
NFC Adapter
===========
Handles NFC tag reading and writing, and NFC device communication.

Supports:
- NFC tag discovery and reading (NDEF, MIFARE, etc.)
- NFC peer-to-peer communication
- NFC card emulation detection
- Smart card interaction

Dependencies:
- nfcpy: For NFC operations (Linux with USB/ACR readers)
- pyscard: For smart card operations (cross-platform)
"""

import threading
import time
from typing import Dict, List, Optional, Callable, Any
from .base_adapter import BaseProtocolAdapter, AdapterState

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from devices.device_registry import (
    Device, DeviceProtocol, DeviceState, DeviceCapability, DeviceMetadata
)


class NFCAdapter(BaseProtocolAdapter):
    """
    NFC adapter for tag reading and device communication.
    Supports multiple NFC reader types and protocols.
    """
    
    # NDEF record type mapping to capabilities
    NDEF_TYPE_CAPABILITIES = {
        'urn:nfc:wkt:U': [],  # URI
        'urn:nfc:wkt:T': [],  # Text
        'urn:nfc:wkt:Sp': [],  # Smart Poster
        'urn:nfc:wkt:Sig': [],  # Signature
        'urn:nfc:wkt:Hc': [],  # Handover Carrier
        'urn:nfc:wkt:Hr': [],  # Handover Request
        'urn:nfc:wkt:Hs': [],  # Handover Select
        'urn:nfc:wkt:ac': [],  # Alternative Carrier
        'urn:nfc:ext:android.com:pkg': [],  # Android Package
    }
    
    # NFC tag types
    TAG_TYPES = {
        1: 'Type 1 Tag (Topaz)',
        2: 'Type 2 Tag (NTAG, MIFARE Ultralight)',
        3: 'Type 3 Tag (FeliCa)',
        4: 'Type 4 Tag (MIFARE DESFire, ISO-DEP)',
        5: 'Type 5 Tag (ISO 15693)',
    }
    
    def __init__(self):
        super().__init__("NFCAdapter")
        self._nfcpy_available = False
        self._pyscard_available = False
        self._reader = None
        self._scan_active = False
        self._last_tag_id: Optional[str] = None
        self._tag_debounce_time = 2.0  # Seconds to wait before re-detecting same tag
        self._last_tag_time = 0
        
    def initialize(self) -> bool:
        """Initialize NFC adapter and detect available readers."""
        self.state = AdapterState.INITIALIZING
        print(f"[{self.name}] Initializing...")
        
        # Try to import nfcpy
        try:
            import nfc
            self._nfcpy_available = True
            print(f"[{self.name}] nfcpy support available")
            
            # Try to find a reader
            reader_path = self._find_nfc_reader()
            if reader_path:
                print(f"[{self.name}] Found NFC reader: {reader_path}")
            else:
                print(f"[{self.name}] No NFC reader found. Connect a USB NFC reader.")
                
        except ImportError:
            print(f"[{self.name}] nfcpy not installed.")
            print(f"[{self.name}] Install with: pip install nfcpy")
        except Exception as e:
            print(f"[{self.name}] nfcpy init error: {e}")
        
        # Try to import pyscard for smart cards
        try:
            from smartcard.System import readers
            from smartcard.CardRequest import CardRequest
            self._pyscard_available = True
            available_readers = readers()
            print(f"[{self.name}] pyscard support available. Readers: {len(available_readers)}")
            for r in available_readers:
                print(f"[{self.name}]   - {r}")
        except ImportError:
            print(f"[{self.name}] pyscard not installed.")
            print(f"[{self.name}] Install with: pip install pyscard")
        except Exception as e:
            print(f"[{self.name}] pyscard init error: {e}")
        
        self._is_available = self._nfcpy_available or self._pyscard_available
        
        if self._is_available:
            self.state = AdapterState.READY
            print(f"[{self.name}] Initialized successfully.")
        else:
            self.state = AdapterState.ERROR
            self._report_error("No NFC libraries available")
            
        return self._is_available
    
    def _find_nfc_reader(self) -> Optional[str]:
        """Find available NFC reader device."""
        try:
            import nfc
            
            # Common USB NFC reader paths
            reader_paths = [
                'usb',  # Auto-detect USB
                'usb:072f:2200',  # ACR122U
                'usb:04e6:5591',  # SCL3711
                'usb:04cc:2533',  # Sony RC-S380
                'usb:054c:06c3',  # Sony RC-S380
                'tty:USB0',  # Serial USB
                'tty:AMA0',  # Raspberry Pi
            ]
            
            for path in reader_paths:
                try:
                    clf = nfc.ContactlessFrontend(path)
                    clf.close()
                    return path
                except Exception:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _nfcpy_scan(self, callback: Callable, duration: float):
        """Scan for NFC tags using nfcpy."""
        try:
            import nfc
            
            reader_path = self._find_nfc_reader()
            if not reader_path:
                self._report_error("No NFC reader available")
                return
            
            def on_connect(tag):
                """Called when a tag is detected."""
                if not self._scan_active:
                    return False
                
                tag_id = tag.identifier.hex() if tag.identifier else "unknown"
                current_time = time.time()
                
                # Debounce same tag detection
                if tag_id == self._last_tag_id and (current_time - self._last_tag_time) < self._tag_debounce_time:
                    return True
                
                self._last_tag_id = tag_id
                self._last_tag_time = current_time
                
                device = self._tag_to_device(tag)
                callback(device)
                
                return True  # Keep reading
            
            clf = nfc.ContactlessFrontend(reader_path)
            print(f"[{self.name}] NFC reader opened. Waiting for tags...")
            
            start_time = time.time()
            while self._scan_active and (time.time() - start_time) < duration:
                try:
                    clf.connect(
                        rdwr={'on-connect': on_connect},
                        terminate=lambda: not self._scan_active
                    )
                except Exception as e:
                    if self._scan_active:
                        time.sleep(0.5)
            
            clf.close()
            print(f"[{self.name}] NFC scan complete.")
            
        except Exception as e:
            self._report_error(f"NFC scan failed: {e}")
    
    def _tag_to_device(self, tag) -> Device:
        """Convert nfcpy tag to Device."""
        tag_id = tag.identifier.hex() if tag.identifier else f"nfc_{time.time()}"
        
        # Determine tag type
        tag_type_str = type(tag).__name__
        
        # Read NDEF data if available
        ndef_data = {}
        capabilities = []
        
        try:
            if hasattr(tag, 'ndef') and tag.ndef:
                ndef_data['message'] = []
                for record in tag.ndef.records:
                    record_info = {
                        'type': record.type,
                        'name': str(record.name) if hasattr(record, 'name') else None,
                    }
                    
                    # Handle different record types
                    if hasattr(record, 'uri'):
                        record_info['uri'] = record.uri
                    if hasattr(record, 'text'):
                        record_info['text'] = record.text
                    if hasattr(record, 'data'):
                        try:
                            record_info['data'] = record.data.decode('utf-8', errors='ignore')
                        except Exception:
                            record_info['data_hex'] = record.data.hex()
                    
                    ndef_data['message'].append(record_info)
                
                ndef_data['capacity'] = tag.ndef.capacity
                ndef_data['is_readable'] = tag.ndef.is_readable
                ndef_data['is_writeable'] = tag.ndef.is_writeable
        except Exception as e:
            ndef_data['error'] = str(e)
        
        # Get product name if available
        product = None
        if hasattr(tag, 'product'):
            product = tag.product
        
        metadata = DeviceMetadata(
            manufacturer=self._get_tag_manufacturer(tag_id),
            model=product,
            serial_number=tag_id,
            last_seen=time.time(),
            custom_data={
                'tag_type': tag_type_str,
                'ndef': ndef_data,
                'identifier_hex': tag_id
            }
        )
        
        return Device(
            id=f"nfc_{tag_id}",
            name=f"NFC Tag {tag_id[-4:]}" if not product else product,
            protocol=DeviceProtocol.NFC,
            state=DeviceState.DISCOVERED,
            address=tag_id,
            capabilities=capabilities,
            metadata=metadata,
            services={'ndef': ndef_data}
        )
    
    def _get_tag_manufacturer(self, uid: str) -> Optional[str]:
        """Get manufacturer from NFC UID."""
        if not uid or len(uid) < 2:
            return None
        
        # First byte is manufacturer ID for some tag types
        MANUFACTURER_IDS = {
            '04': 'NXP Semiconductors',
            '05': 'Infineon Technologies',
            '16': 'Texas Instruments',
            '1F': 'Sony',
            '02': 'STMicroelectronics',
            '07': 'Vishay',
            '12': 'Atmel',
        }
        
        return MANUFACTURER_IDS.get(uid[:2].upper())
    
    def _pyscard_scan(self, callback: Callable, duration: float):
        """Scan for smart cards using pyscard."""
        try:
            from smartcard.System import readers
            from smartcard.CardRequest import CardRequest
            from smartcard.util import toHexString
            
            available_readers = readers()
            if not available_readers:
                print(f"[{self.name}] No smart card readers found")
                return
            
            print(f"[{self.name}] Scanning with {len(available_readers)} reader(s)...")
            
            start_time = time.time()
            seen_cards = set()
            
            while self._scan_active and (time.time() - start_time) < duration:
                for reader in available_readers:
                    try:
                        connection = reader.createConnection()
                        connection.connect()
                        
                        # Get card ATR (Answer To Reset)
                        atr = toHexString(connection.getATR())
                        
                        if atr not in seen_cards:
                            seen_cards.add(atr)
                            device = self._smartcard_to_device(reader, connection, atr)
                            callback(device)
                        
                        connection.disconnect()
                        
                    except Exception:
                        pass  # No card in reader
                
                time.sleep(0.5)
            
            print(f"[{self.name}] Smart card scan complete.")
            
        except Exception as e:
            self._report_error(f"Smart card scan failed: {e}")
    
    def _smartcard_to_device(self, reader, connection, atr: str) -> Device:
        """Convert smart card to Device."""
        # Try to get card UID
        uid = None
        try:
            # ISO 14443-3A Get UID command
            GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            response, sw1, sw2 = connection.transmit(GET_UID)
            if sw1 == 0x90 and sw2 == 0x00:
                uid = ''.join(format(x, '02X') for x in response)
        except Exception:
            uid = atr.replace(' ', '')[:16]
        
        device_id = f"sc_{uid}" if uid else f"sc_{atr.replace(' ', '')[:16]}"
        
        metadata = DeviceMetadata(
            last_seen=time.time(),
            custom_data={
                'atr': atr,
                'reader': str(reader),
                'uid': uid
            }
        )
        
        return Device(
            id=device_id,
            name=f"Smart Card {uid[-4:] if uid else 'Unknown'}",
            protocol=DeviceProtocol.NFC,
            state=DeviceState.DISCOVERED,
            address=uid or atr,
            capabilities=[],
            metadata=metadata,
            services={'smartcard': {'atr': atr, 'uid': uid}}
        )
    
    def start_discovery(self, callback: Callable, duration: float = 30.0) -> bool:
        """Start NFC tag/card discovery."""
        if not self._is_available:
            self._report_error("NFC not available")
            return False
        
        if self._scan_active:
            print(f"[{self.name}] Scan already in progress.")
            return False
        
        self._scan_active = True
        self._last_tag_id = None
        self.state = AdapterState.SCANNING
        
        def scan_thread():
            try:
                if self._nfcpy_available:
                    self._nfcpy_scan(callback, duration)
                elif self._pyscard_available:
                    self._pyscard_scan(callback, duration)
            except Exception as e:
                self._report_error(f"Scan error: {e}")
            finally:
                self._scan_active = False
                self.state = AdapterState.READY
        
        self._scan_thread = threading.Thread(target=scan_thread, daemon=True)
        self._scan_thread.start()
        
        return True
    
    def stop_discovery(self):
        """Stop NFC scanning."""
        self._scan_active = False
        if self._scan_thread and self._scan_thread.is_alive():
            self._scan_thread.join(timeout=2.0)
        self.state = AdapterState.READY
        print(f"[{self.name}] Discovery stopped.")
    
    def connect(self, device_id: str) -> bool:
        """Connect to an NFC device (keep tag in field)."""
        print(f"[{self.name}] NFC tags require physical proximity")
        return True
    
    def disconnect(self, device_id: str) -> bool:
        """Disconnect from NFC device."""
        return True
    
    def read_tag(self, timeout: float = 10.0) -> Optional[Dict[str, Any]]:
        """Read an NFC tag and return its data."""
        if not self._nfcpy_available:
            self._report_error("nfcpy required for tag reading")
            return None
        
        try:
            import nfc
            
            reader_path = self._find_nfc_reader()
            if not reader_path:
                return None
            
            result = {'success': False}
            
            def on_connect(tag):
                result['success'] = True
                result['tag_id'] = tag.identifier.hex() if tag.identifier else None
                result['type'] = type(tag).__name__
                
                if hasattr(tag, 'ndef') and tag.ndef:
                    result['ndef'] = {
                        'capacity': tag.ndef.capacity,
                        'records': []
                    }
                    for record in tag.ndef.records:
                        rec = {'type': record.type}
                        if hasattr(record, 'uri'):
                            rec['uri'] = record.uri
                        if hasattr(record, 'text'):
                            rec['text'] = record.text
                        result['ndef']['records'].append(rec)
                
                return False  # Stop after first read
            
            clf = nfc.ContactlessFrontend(reader_path)
            clf.connect(rdwr={'on-connect': on_connect}, terminate=lambda: False)
            clf.close()
            
            return result if result['success'] else None
            
        except Exception as e:
            self._report_error(f"Tag read failed: {e}")
            return None
    
    def write_tag(self, data: Dict[str, Any], timeout: float = 10.0) -> bool:
        """Write NDEF data to an NFC tag."""
        if not self._nfcpy_available:
            self._report_error("nfcpy required for tag writing")
            return False
        
        try:
            import nfc
            import nfc.ndef
            
            reader_path = self._find_nfc_reader()
            if not reader_path:
                return False
            
            # Build NDEF message
            records = []
            
            if 'uri' in data:
                records.append(nfc.ndef.UriRecord(data['uri']))
            if 'text' in data:
                records.append(nfc.ndef.TextRecord(data['text']))
            
            if not records:
                self._report_error("No valid NDEF data provided")
                return False
            
            message = nfc.ndef.Message(*records)
            success = False
            
            def on_connect(tag):
                nonlocal success
                if tag.ndef and tag.ndef.is_writeable:
                    tag.ndef.records = message
                    success = True
                    print(f"[{self.name}] Tag written successfully")
                else:
                    print(f"[{self.name}] Tag not writeable")
                return False
            
            clf = nfc.ContactlessFrontend(reader_path)
            print(f"[{self.name}] Place tag on reader to write...")
            clf.connect(rdwr={'on-connect': on_connect}, terminate=lambda: False)
            clf.close()
            
            return success
            
        except Exception as e:
            self._report_error(f"Tag write failed: {e}")
            return False
    
    def send_data(self, device_id: str, data: bytes) -> bool:
        """Send data to NFC device (APDU commands)."""
        # Would need active connection
        return False
    
    def receive_data(self, device_id: str, timeout: float = 5.0) -> Optional[bytes]:
        """Receive data from NFC device."""
        return None
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get NFC device information."""
        return None
    
    def shutdown(self):
        """Shutdown the NFC adapter."""
        self.stop_discovery()
        super().shutdown()
