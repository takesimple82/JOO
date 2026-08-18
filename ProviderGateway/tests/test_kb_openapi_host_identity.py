from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from ProviderGateway.auth.credentials import SECRET_FIELD_NAMES
from ProviderGateway.auth.kb_openapi_host_identity import (
    HOST_IDENTITY_FILENAME,
    KbOpenApiHostIdentity,
    default_kb_openapi_host_identity_path,
    delete_kb_openapi_host_identity,
    derive_active_primary_wifi_mac,
    format_link_mac,
    is_usable_ip_addr,
    is_usable_mac_addr,
    load_kb_openapi_host_identity,
    resolve_kb_openapi_host_identity,
    select_active_wifi_link_mac,
    write_kb_openapi_host_identity,
)


FAKE_IP = "203.0.113.10"
FAKE_MAC = "02:c9:e7:ea:c3:8a"
WIFI_ID = "ac:c9:06:24:5a:ba"
AP_BSSID = "aa:aa:aa:aa:aa:aa"
ETHERNET_MAC = "11:22:33:44:55:66"
HOST_PATH = (
    Path(__file__).resolve().parents[1]
    / "auth"
    / "kb_openapi_host_identity.py"
)


class HostFileContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / HOST_IDENTITY_FILENAME
        self.real_joo = Path.home() / ".joo"
        self.real_existed = self.real_joo.exists()

    def tearDown(self):
        self.tmp.cleanup()
        if not self.real_existed:
            self.assertFalse(self.real_joo.exists())

    def test_valid_ip_only_round_trip(self):
        self.assertTrue(
            write_kb_openapi_host_identity(self.path, FAKE_IP)
        )
        loaded = load_kb_openapi_host_identity(self.path)
        self.assertEqual(loaded, KbOpenApiHostIdentity(FAKE_IP, None))
        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            '{"ip_addr":"203.0.113.10"}',
        )

    def test_valid_ip_and_mac_round_trip(self):
        self.assertTrue(
            write_kb_openapi_host_identity(
                self.path,
                FAKE_IP,
                FAKE_MAC,
            )
        )
        loaded = load_kb_openapi_host_identity(self.path)
        self.assertEqual(
            loaded,
            KbOpenApiHostIdentity(FAKE_IP, FAKE_MAC),
        )
        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            '{"ip_addr":"203.0.113.10","mac_addr":"02:c9:e7:ea:c3:8a"}',
        )

    def test_malformed_and_non_object_json(self):
        cases = ("{", "[]", "null", '"x"', "1")
        for raw in cases:
            self.path.write_text(raw, encoding="utf-8")
            with self.subTest(raw=raw):
                self.assertIsNone(
                    load_kb_openapi_host_identity(self.path)
                )

    def test_extra_keys_rejected(self):
        self.path.write_text(
            json.dumps(
                {"ip_addr": FAKE_IP, "extra": "1"},
                separators=(",", ":"),
            ),
            encoding="utf-8",
        )
        self.assertIsNone(load_kb_openapi_host_identity(self.path))

    def test_secret_keys_rejected(self):
        for name in SECRET_FIELD_NAMES:
            payload = {"ip_addr": FAKE_IP, name: "x"}
            self.path.write_text(
                json.dumps(payload, separators=(",", ":")),
                encoding="utf-8",
            )
            with self.subTest(name=name):
                self.assertIsNone(
                    load_kb_openapi_host_identity(self.path)
                )

    def test_missing_file_is_none(self):
        self.assertIsNone(load_kb_openapi_host_identity(self.path))

    def test_delete_already_absent_is_lawful(self):
        self.assertTrue(delete_kb_openapi_host_identity(self.path))
        write_kb_openapi_host_identity(self.path, FAKE_IP)
        self.assertTrue(delete_kb_openapi_host_identity(self.path))
        self.assertFalse(self.path.exists())

    def test_safe_write_permissions(self):
        self.assertTrue(
            write_kb_openapi_host_identity(self.path, FAKE_IP)
        )
        dir_mode = stat.S_IMODE(os.stat(self.path.parent).st_mode)
        file_mode = stat.S_IMODE(os.stat(self.path).st_mode)
        self.assertEqual(dir_mode, 0o700)
        self.assertEqual(file_mode, 0o600)
        self.assertFalse((self.path.parent / (self.path.name + ".tmp")).exists())

    def test_default_path_identity(self):
        self.assertEqual(
            default_kb_openapi_host_identity_path(),
            Path.home() / ".joo" / HOST_IDENTITY_FILENAME,
        )

    def test_no_profile_or_credential_ref_persisted(self):
        write_kb_openapi_host_identity(self.path, FAKE_IP, FAKE_MAC)
        raw = self.path.read_text(encoding="utf-8")
        parsed = json.loads(raw)
        self.assertEqual(set(parsed), {"ip_addr", "mac_addr"})
        self.assertNotIn("profile_id", raw)
        self.assertNotIn("account_selector", raw)
        self.assertNotIn("credential_ref", raw)


class IpValidationTests(unittest.TestCase):
    def test_ip_required_and_placeholders_rejected(self):
        self.assertTrue(is_usable_ip_addr(FAKE_IP))
        self.assertFalse(is_usable_ip_addr(""))
        self.assertFalse(is_usable_ip_addr(" 203.0.113.10"))
        self.assertFalse(is_usable_ip_addr("203.0.113.10 "))
        self.assertFalse(is_usable_ip_addr("   "))
        self.assertFalse(is_usable_ip_addr("127.0.0.1"))
        self.assertFalse(is_usable_ip_addr("0.0.0.0"))
        self.assertFalse(is_usable_ip_addr(1))
        self.assertFalse(is_usable_ip_addr(None))

    def test_write_rejects_invalid_ip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / HOST_IDENTITY_FILENAME
            self.assertFalse(
                write_kb_openapi_host_identity(path, "127.0.0.1")
            )
            self.assertFalse(path.exists())


class MacOverrideTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / HOST_IDENTITY_FILENAME
        self.real_joo = Path.home() / ".joo"
        self.real_existed = self.real_joo.exists()

    def tearDown(self):
        self.tmp.cleanup()
        if not self.real_existed:
            self.assertFalse(self.real_joo.exists())

    def test_override_used_and_deriver_not_called(self):
        write_kb_openapi_host_identity(self.path, FAKE_IP, FAKE_MAC)
        called = {"n": 0}

        def boom():
            called["n"] += 1
            raise AssertionError("deriver must not run")

        resolved = resolve_kb_openapi_host_identity(self.path, boom)
        self.assertEqual(resolved.mac_addr, FAKE_MAC)
        self.assertEqual(called["n"], 0)

    def test_invalid_override_does_not_derive(self):
        self.path.write_text(
            '{"ip_addr":"203.0.113.10","mac_addr":"00:00:00:00:00:00"}',
            encoding="utf-8",
        )
        called = {"n": 0}

        def boom():
            called["n"] += 1
            return FAKE_MAC

        self.assertIsNone(
            resolve_kb_openapi_host_identity(self.path, boom)
        )
        self.assertEqual(called["n"], 0)

    def test_placeholder_and_uppercase_mac_rejected(self):
        self.assertTrue(is_usable_mac_addr(FAKE_MAC))
        self.assertFalse(is_usable_mac_addr("00:00:00:00:00:00"))
        self.assertFalse(is_usable_mac_addr("02:C9:E7:EA:C3:8A"))
        self.assertFalse(is_usable_mac_addr("02-c9-e7-ea-c3-8a"))
        self.assertFalse(is_usable_mac_addr(" 02:c9:e7:ea:c3:8a"))
        self.assertFalse(is_usable_mac_addr(""))


class MacDerivationTests(unittest.TestCase):
    def test_format_is_lowercase_colon_hex(self):
        formatted = format_link_mac(bytes.fromhex("02c9e7eac38a"))
        self.assertEqual(formatted, FAKE_MAC)
        self.assertIsNone(format_link_mac(bytes.fromhex("000000000000")))
        self.assertIsNone(format_link_mac(b"\x01\x02"))

    def test_auto_derived_active_wifi_local_mac(self):
        mac = derive_active_primary_wifi_mac(
            list_ieee80211_bsd_names=lambda: ("en1",),
            read_hint_interface=lambda: "en1",
            list_link_interfaces=lambda: (
                ("en1", True, bytes.fromhex("02c9e7eac38a")),
            ),
        )
        self.assertEqual(mac, FAKE_MAC)

    def test_private_wifi_mac_accepted(self):
        mac = select_active_wifi_link_mac(
            ("wlan0",),
            "wlan0",
            (("wlan0", True, bytes.fromhex("02c9e7eac38a")),),
        )
        self.assertEqual(mac, FAKE_MAC)
        self.assertEqual(mac[0:2], "02")

    def test_ethernet_hint_plus_one_up_wifi_uses_wifi(self):
        mac = select_active_wifi_link_mac(
            ("en1",),
            "en0",
            (
                ("en0", True, bytes.fromhex("112233445566")),
                ("en1", True, bytes.fromhex("02c9e7eac38a")),
            ),
        )
        self.assertEqual(mac, FAKE_MAC)
        self.assertNotEqual(mac, ETHERNET_MAC)

    def test_no_en0_only_default(self):
        mac = select_active_wifi_link_mac(
            ("wlan1",),
            None,
            (
                ("en0", True, bytes.fromhex("aaaaaaaaaaaa")),
                ("wlan1", True, bytes.fromhex("02c9e7eac38a")),
            ),
        )
        self.assertEqual(mac, FAKE_MAC)

    def test_multiple_up_wifi_without_hint_match_fails(self):
        mac = select_active_wifi_link_mac(
            ("en1", "en2"),
            "en0",
            (
                ("en1", True, bytes.fromhex("02c9e7eac38a")),
                ("en2", True, bytes.fromhex("02aabbccddee")),
            ),
        )
        self.assertIsNone(mac)

    def test_hint_wifi_is_preferred_among_several(self):
        mac = select_active_wifi_link_mac(
            ("en1", "en2"),
            "en2",
            (
                ("en1", True, bytes.fromhex("02c9e7eac38a")),
                ("en2", True, bytes.fromhex("02aabbccddee")),
            ),
        )
        self.assertEqual(mac, "02:aa:bb:cc:dd:ee")

    def test_down_wifi_is_not_selected(self):
        mac = select_active_wifi_link_mac(
            ("en1",),
            "en1",
            (("en1", False, bytes.fromhex("02c9e7eac38a")),),
        )
        self.assertIsNone(mac)

    def test_derive_fail_without_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / HOST_IDENTITY_FILENAME
            write_kb_openapi_host_identity(path, FAKE_IP)
            resolved = resolve_kb_openapi_host_identity(
                path,
                lambda: None,
            )
            self.assertIsNone(resolved)

    def test_source_rejects_wifi_id_and_bssid_mechanisms(self):
        source = HOST_PATH.read_text()
        for forbidden in (
            "networksetup",
            "SCNetworkInterfaceGetHardwareAddressString",
            "BSSID",
            "CoreWLAN",
            "ifconfig",
        ):
            self.assertNotIn(forbidden, source)
        self.assertNotIn('"en0"', source)
        self.assertIn("getifaddrs", source)
        self.assertIn("IEEE80211", source)

    def test_wifi_id_and_ap_bssid_are_not_algorithm_inputs(self):
        mac = select_active_wifi_link_mac(
            ("en1",),
            "en1",
            (("en1", True, bytes.fromhex("02c9e7eac38a")),),
        )
        self.assertEqual(mac, FAKE_MAC)
        self.assertNotEqual(mac, WIFI_ID)
        self.assertNotEqual(mac, AP_BSSID)


class IsolationTests(unittest.TestCase):
    def test_tests_do_not_create_real_joo(self):
        real = Path.home() / ".joo"
        existed = real.exists()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / HOST_IDENTITY_FILENAME
            write_kb_openapi_host_identity(path, FAKE_IP)
            load_kb_openapi_host_identity(path)
        if not existed:
            self.assertFalse(real.exists())

    def test_source_forbids_external_ip_and_secret_tools(self):
        source = HOST_PATH.read_text()
        for forbidden in (
            "subprocess",
            "keyring",
            "requests",
            "httpx",
            "socket.gethostbyname",
            "urllib",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
