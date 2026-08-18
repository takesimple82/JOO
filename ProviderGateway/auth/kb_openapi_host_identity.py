from __future__ import annotations

import json
import os
import pathlib
from dataclasses import dataclass

from ProviderGateway.auth.credentials import (
    SECRET_FIELD_NAMES,
    is_secret_field_name,
)

HOST_IDENTITY_FILENAME = "kb_openapi_host_identity.json"
_PLACEHOLDER_IP_LOOPBACK = "127.0.0.1"
_PLACEHOLDER_IP_ANY = "0.0.0.0"
_PLACEHOLDER_MAC = "00:00:00:00:00:00"
_HEX_LOWER = "0123456789abcdef"
_CF_STRING_ENCODING_UTF8 = 0x08000100
_IFF_UP = 0x1
_AF_LINK = 18
_SYSTEM_CONFIGURATION = (
    "/System/Library/Frameworks/SystemConfiguration.framework/"
    "SystemConfiguration"
)
_COREFOUNDATION_FRAMEWORK = (
    "/System/Library/Frameworks/CoreFoundation.framework/"
    "CoreFoundation"
)
_LIBSYSTEM = "/usr/lib/libSystem.B.dylib"


@dataclass(frozen=True)
class KbOpenApiHostIdentity:
    ip_addr: str
    mac_addr: str | None


def default_kb_openapi_host_identity_path():
    return pathlib.Path.home() / ".joo" / HOST_IDENTITY_FILENAME


def is_usable_ip_addr(value) -> bool:
    if type(value) is not str:
        return False
    if value == "":
        return False
    if value != value.strip():
        return False
    if value == _PLACEHOLDER_IP_LOOPBACK:
        return False
    if value == _PLACEHOLDER_IP_ANY:
        return False
    return True


def is_usable_mac_addr(value) -> bool:
    if type(value) is not str:
        return False
    if value == "":
        return False
    if value != value.strip():
        return False
    if value == _PLACEHOLDER_MAC:
        return False
    parts = value.split(":")
    if len(parts) != 6:
        return False
    for part in parts:
        if len(part) != 2:
            return False
        for char in part:
            if char not in _HEX_LOWER:
                return False
    return True


def format_link_mac(mac_octets):
    if type(mac_octets) is not bytes:
        return None
    if len(mac_octets) != 6:
        return None
    parts = []
    for octet in mac_octets:
        parts.append("%02x" % octet)
    formatted = ":".join(parts)
    if formatted == _PLACEHOLDER_MAC:
        return None
    return formatted


def select_active_wifi_link_mac(
    ieee80211_names,
    hint_interface,
    link_interfaces,
):
    if type(ieee80211_names) is not tuple:
        if type(ieee80211_names) is not list:
            return None
    wifi_names = set()
    for name in ieee80211_names:
        if type(name) is not str:
            continue
        if name == "":
            continue
        wifi_names.add(name)
    eligible = {}
    for item in link_interfaces:
        if type(item) is not tuple or len(item) != 3:
            continue
        name, is_up, mac_octets = item
        if name not in wifi_names:
            continue
        if is_up is not True:
            continue
        formatted = format_link_mac(mac_octets)
        if formatted is None:
            continue
        eligible[name] = formatted
    if (
        type(hint_interface) is str
        and hint_interface in eligible
    ):
        return eligible[hint_interface]
    if len(eligible) == 1:
        return next(iter(eligible.values()))
    return None


def derive_active_primary_wifi_mac(
    list_ieee80211_bsd_names=None,
    read_hint_interface=None,
    list_link_interfaces=None,
):
    if list_ieee80211_bsd_names is None:
        list_ieee80211_bsd_names = _production_list_ieee80211_bsd_names
    if read_hint_interface is None:
        read_hint_interface = _production_read_hint_interface
    if list_link_interfaces is None:
        list_link_interfaces = _production_list_link_interfaces
    try:
        names = list_ieee80211_bsd_names()
        hint = read_hint_interface()
        links = list_link_interfaces()
    except Exception:
        return None
    return select_active_wifi_link_mac(names, hint, links)


def _as_host_path(path):
    if type(path) is str or isinstance(path, pathlib.Path):
        return pathlib.Path(path)
    return None


def load_kb_openapi_host_identity(path):
    path = _as_host_path(path)
    if path is None:
        return None
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return None
    for name in SECRET_FIELD_NAMES:
        if name in raw:
            return None
    try:
        parsed = json.loads(raw)
    except ValueError:
        return None
    if type(parsed) is not dict:
        return None
    keys = set(parsed.keys())
    if "ip_addr" not in keys:
        return None
    allowed = {"ip_addr", "mac_addr"}
    if not keys.issubset(allowed):
        return None
    for key in keys:
        if is_secret_field_name(key):
            return None
        if type(parsed[key]) is not str:
            return None
    ip_addr = parsed["ip_addr"]
    if not is_usable_ip_addr(ip_addr):
        return None
    mac_addr = None
    if "mac_addr" in parsed:
        mac_addr = parsed["mac_addr"]
        if not is_usable_mac_addr(mac_addr):
            return None
    return KbOpenApiHostIdentity(ip_addr, mac_addr)


def write_kb_openapi_host_identity(path, ip_addr, mac_addr=None):
    if not is_usable_ip_addr(ip_addr):
        return False
    if mac_addr is not None and not is_usable_mac_addr(mac_addr):
        return False
    path = _as_host_path(path)
    if path is None:
        return False
    payload = {"ip_addr": ip_addr}
    if mac_addr is not None:
        payload["mac_addr"] = mac_addr
    text = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    directory = path.parent
    temp_path = path.with_name(path.name + ".tmp")
    fd = None
    try:
        os.makedirs(directory, mode=0o700, exist_ok=True)
        os.chmod(directory, 0o700)
        if temp_path.exists():
            os.unlink(temp_path)
        fd = os.open(
            temp_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd = None
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        os.chmod(path, 0o600)
        return True
    except OSError:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            if temp_path.exists():
                os.unlink(temp_path)
        except OSError:
            pass
        return False


def delete_kb_openapi_host_identity(path):
    path = _as_host_path(path)
    if path is None:
        return False
    try:
        if not path.exists():
            return True
        os.unlink(path)
        return not path.exists()
    except OSError:
        return False


def resolve_kb_openapi_host_identity(path, mac_deriver):
    loaded = load_kb_openapi_host_identity(path)
    if loaded is None:
        return None
    if loaded.mac_addr is not None:
        if not is_usable_mac_addr(loaded.mac_addr):
            return None
        return loaded
    if not callable(mac_deriver):
        return None
    try:
        derived = mac_deriver()
    except Exception:
        return None
    if not is_usable_mac_addr(derived):
        return None
    return KbOpenApiHostIdentity(loaded.ip_addr, derived)


def _cfstring_to_py(cf, ref):
    if not ref:
        return None
    import ctypes

    buf = ctypes.create_string_buffer(256)
    ok = cf.CFStringGetCString(
        ref,
        buf,
        256,
        _CF_STRING_ENCODING_UTF8,
    )
    if not ok:
        return None
    return buf.value.decode("utf-8")


def _production_list_ieee80211_bsd_names():
    import ctypes

    try:
        cf = ctypes.CDLL(_COREFOUNDATION_FRAMEWORK)
        sc = ctypes.CDLL(_SYSTEM_CONFIGURATION)
        cf.CFArrayGetCount.argtypes = [ctypes.c_void_p]
        cf.CFArrayGetCount.restype = ctypes.c_long
        cf.CFArrayGetValueAtIndex.argtypes = [
            ctypes.c_void_p,
            ctypes.c_long,
        ]
        cf.CFArrayGetValueAtIndex.restype = ctypes.c_void_p
        cf.CFStringGetCString.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_long,
            ctypes.c_uint32,
        ]
        cf.CFStringGetCString.restype = ctypes.c_bool
        cf.CFRelease.argtypes = [ctypes.c_void_p]
        cf.CFRelease.restype = None
        sc.SCNetworkInterfaceCopyAll.argtypes = []
        sc.SCNetworkInterfaceCopyAll.restype = ctypes.c_void_p
        sc.SCNetworkInterfaceGetInterfaceType.argtypes = [
            ctypes.c_void_p
        ]
        sc.SCNetworkInterfaceGetInterfaceType.restype = (
            ctypes.c_void_p
        )
        sc.SCNetworkInterfaceGetBSDName.argtypes = [ctypes.c_void_p]
        sc.SCNetworkInterfaceGetBSDName.restype = ctypes.c_void_p
        expected = _cfstring_to_py(
            cf,
            ctypes.c_void_p.in_dll(
                sc,
                "kSCNetworkInterfaceTypeIEEE80211",
            ).value,
        )
        if expected is None:
            return ()
        array = sc.SCNetworkInterfaceCopyAll()
        if not array:
            return ()
        names = []
        try:
            count = int(cf.CFArrayGetCount(array))
            for index in range(count):
                iface = cf.CFArrayGetValueAtIndex(array, index)
                kind = _cfstring_to_py(
                    cf,
                    sc.SCNetworkInterfaceGetInterfaceType(iface),
                )
                if kind != expected:
                    continue
                name = _cfstring_to_py(
                    cf,
                    sc.SCNetworkInterfaceGetBSDName(iface),
                )
                if type(name) is str and name != "":
                    names.append(name)
        finally:
            cf.CFRelease(array)
        return tuple(names)
    except Exception:
        return ()


def _production_read_hint_interface():
    import ctypes

    created = []
    try:
        cf = ctypes.CDLL(_COREFOUNDATION_FRAMEWORK)
        sc = ctypes.CDLL(_SYSTEM_CONFIGURATION)
        cf.CFStringCreateWithCString.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_uint32,
        ]
        cf.CFStringCreateWithCString.restype = ctypes.c_void_p
        cf.CFStringGetCString.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_long,
            ctypes.c_uint32,
        ]
        cf.CFStringGetCString.restype = ctypes.c_bool
        cf.CFDictionaryGetValue.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        cf.CFDictionaryGetValue.restype = ctypes.c_void_p
        cf.CFRelease.argtypes = [ctypes.c_void_p]
        cf.CFRelease.restype = None
        sc.SCDynamicStoreCreate.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        sc.SCDynamicStoreCreate.restype = ctypes.c_void_p
        sc.SCDynamicStoreCopyValue.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        sc.SCDynamicStoreCopyValue.restype = ctypes.c_void_p
        allocator = ctypes.c_void_p.in_dll(
            cf,
            "kCFAllocatorDefault",
        ).value
        store_name = cf.CFStringCreateWithCString(
            allocator,
            b"joo.kb.openapi",
            _CF_STRING_ENCODING_UTF8,
        )
        if not store_name:
            return None
        created.append(store_name)
        key = cf.CFStringCreateWithCString(
            allocator,
            b"State:/Network/Global/IPv4",
            _CF_STRING_ENCODING_UTF8,
        )
        if not key:
            return None
        created.append(key)
        field = cf.CFStringCreateWithCString(
            allocator,
            b"PrimaryInterface",
            _CF_STRING_ENCODING_UTF8,
        )
        if not field:
            return None
        created.append(field)
        store = sc.SCDynamicStoreCreate(
            allocator,
            store_name,
            None,
            None,
        )
        if not store:
            return None
        created.append(store)
        value = sc.SCDynamicStoreCopyValue(store, key)
        if not value:
            return None
        created.append(value)
        hint_ref = cf.CFDictionaryGetValue(value, field)
        return _cfstring_to_py(cf, hint_ref)
    except Exception:
        return None
    finally:
        try:
            cf = ctypes.CDLL(_COREFOUNDATION_FRAMEWORK)
            cf.CFRelease.argtypes = [ctypes.c_void_p]
            cf.CFRelease.restype = None
            for ref in reversed(created):
                if ref:
                    cf.CFRelease(ref)
        except Exception:
            pass


def _production_list_link_interfaces():
    import ctypes

    class _Ifaddrs(ctypes.Structure):
        pass

    _Ifaddrs._fields_ = [
        ("ifa_next", ctypes.POINTER(_Ifaddrs)),
        ("ifa_name", ctypes.c_char_p),
        ("ifa_flags", ctypes.c_uint),
        ("ifa_addr", ctypes.c_void_p),
        ("ifa_netmask", ctypes.c_void_p),
        ("ifa_dstaddr", ctypes.c_void_p),
        ("ifa_data", ctypes.c_void_p),
    ]

    class _Sockaddr(ctypes.Structure):
        _fields_ = [
            ("sa_len", ctypes.c_uint8),
            ("sa_family", ctypes.c_uint8),
        ]

    class _SockaddrDl(ctypes.Structure):
        _fields_ = [
            ("sdl_len", ctypes.c_uint8),
            ("sdl_family", ctypes.c_uint8),
            ("sdl_index", ctypes.c_uint16),
            ("sdl_type", ctypes.c_uint8),
            ("sdl_nlen", ctypes.c_uint8),
            ("sdl_alen", ctypes.c_uint8),
            ("sdl_slen", ctypes.c_uint8),
            ("sdl_data", ctypes.c_uint8 * 12),
        ]

    try:
        libc = ctypes.CDLL(_LIBSYSTEM)
        libc.getifaddrs.argtypes = [
            ctypes.POINTER(ctypes.POINTER(_Ifaddrs))
        ]
        libc.getifaddrs.restype = ctypes.c_int
        libc.freeifaddrs.argtypes = [ctypes.POINTER(_Ifaddrs)]
        libc.freeifaddrs.restype = None
        head = ctypes.POINTER(_Ifaddrs)()
        if libc.getifaddrs(ctypes.byref(head)) != 0:
            return ()
        found = []
        try:
            current = head
            while current:
                node = current.contents
                raw_name = node.ifa_name
                if raw_name is None:
                    current = node.ifa_next
                    continue
                name = raw_name.decode("utf-8", "replace")
                is_up = (node.ifa_flags & _IFF_UP) != 0
                mac = None
                if node.ifa_addr:
                    sa = ctypes.cast(
                        node.ifa_addr,
                        ctypes.POINTER(_Sockaddr),
                    ).contents
                    if sa.sa_family == _AF_LINK:
                        sdl = ctypes.cast(
                            node.ifa_addr,
                            ctypes.POINTER(_SockaddrDl),
                        ).contents
                        if sdl.sdl_alen == 6:
                            offset = (
                                _SockaddrDl.sdl_data.offset
                                + sdl.sdl_nlen
                            )
                            mac = ctypes.string_at(
                                node.ifa_addr + offset,
                                6,
                            )
                found.append((name, is_up, mac))
                current = node.ifa_next
        finally:
            libc.freeifaddrs(head)
        return tuple(found)
    except Exception:
        return ()
