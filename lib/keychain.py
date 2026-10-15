"""macOS Keychain access through Security.framework; no shell or password argv."""
import ctypes as C
import hashlib
import json
import sys


def account(profile):
    identity = [profile.get('host', '').lower(), int(profile.get('port', 21)),
                profile.get('protocol', 'ftps'), profile.get('username', 'anonymous')]
    return hashlib.sha256(json.dumps(identity).encode('utf-8')).hexdigest().encode('ascii')


def access(profile, password=None):
    if sys.platform != 'darwin':
        return None
    sec = C.CDLL('/System/Library/Frameworks/Security.framework/Security')
    core = C.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
    ptr = C.c_void_p
    uint = C.c_uint32
    sec.SecKeychainFindGenericPassword.argtypes = [ptr, uint, C.c_char_p, uint, C.c_char_p,
                                                  C.POINTER(uint), C.POINTER(ptr), C.POINTER(ptr)]
    sec.SecKeychainFindGenericPassword.restype = C.c_int32
    sec.SecKeychainAddGenericPassword.argtypes = [ptr, uint, C.c_char_p, uint, C.c_char_p,
                                                 uint, C.c_char_p, C.POINTER(ptr)]
    sec.SecKeychainAddGenericPassword.restype = C.c_int32
    sec.SecKeychainItemModifyAttributesAndData.argtypes = [ptr, ptr, uint, C.c_char_p]
    sec.SecKeychainItemModifyAttributesAndData.restype = C.c_int32
    sec.SecKeychainItemFreeContent.argtypes = [ptr, ptr]
    core.CFRelease.argtypes = [ptr]
    service = b'RemoteTreeFTP'
    user = account(profile)
    size, data, item = uint(), ptr(), ptr()
    code = sec.SecKeychainFindGenericPassword(None, len(service), service, len(user), user,
                                            C.byref(size), C.byref(data), C.byref(item))
    try:
        if code not in (0, -25300):
            raise RuntimeError('Keychain: {}'.format(code))
        if password is None:
            return C.string_at(data, size.value).decode('utf-8') if code == 0 else None
        encoded = password.encode('utf-8')
        if code == 0:
            result = sec.SecKeychainItemModifyAttributesAndData(item, None, len(encoded), encoded)
        else:
            result = sec.SecKeychainAddGenericPassword(None, len(service), service, len(user), user,
                                                      len(encoded), encoded, None)
        if result:
            raise RuntimeError('Keychain: {}'.format(result))
    finally:
        if data.value:
            sec.SecKeychainItemFreeContent(None, data)
        if item.value:
            core.CFRelease(item)
