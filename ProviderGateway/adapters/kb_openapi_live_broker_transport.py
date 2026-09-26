from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from ProviderGateway.adapters.ports import (
    ExplicitHealthProbe,
    ExplicitTransportFailure,
    ExplicitTransportSuccess,
)
from ProviderGateway.auth.credentials import SECRET_FIELD_NAMES
from ProviderGateway.models.types import (
    ExplicitBrokerAdapterBinding,
    ExplicitBrokerCollectRequest,
)


DEFAULT_BASE_URL = "https://developer.kbsec.com:32484"
TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS = 60
_ALLOWED_EXCG_MKTPR_CCD = ("", "A", "K", "N")
_CREDENTIAL_KEYS = frozenset({"appKey", "appSecret"})
_FORBIDDEN_SECRET_KEYS = frozenset(SECRET_FIELD_NAMES)
_UNAUTHORIZED = object()


@dataclass(frozen=True)
class KbOpenApiHttpResponse:
    status_code: int
    body_text: str


def decode_kb_openapi_client_material(credential: object):
    if type(credential) is not str:
        return None
    try:
        parsed = json.loads(credential)
    except ValueError:
        return None
    if type(parsed) is not dict:
        return None
    if set(parsed.keys()) != _CREDENTIAL_KEYS:
        return None
    app_key = parsed["appKey"]
    app_secret = parsed["appSecret"]
    if type(app_key) is not str or type(app_secret) is not str:
        return None
    if app_key == "" or app_secret == "":
        return None
    return (app_key, app_secret)


def _serialize_compact_json(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _auth_failure() -> ExplicitTransportFailure:
    return ExplicitTransportFailure("AUTH_FAILURE", None)


def _validation_failure() -> ExplicitTransportFailure:
    return ExplicitTransportFailure("VALIDATION_FAILURE", None)


def _provider_error() -> ExplicitTransportFailure:
    return ExplicitTransportFailure("PROVIDER_ERROR", None)


def _rate_limited() -> ExplicitTransportFailure:
    return ExplicitTransportFailure("RATE_LIMITED", None)


def _transport_failure() -> ExplicitTransportFailure:
    return ExplicitTransportFailure("TRANSPORT_FAILURE", None)


def _residual_secret_values(*values):
    secrets = []
    for value in values:
        if type(value) is str and value != "":
            secrets.append(value)
    return tuple(secrets)


def _payload_contains_residual_secret(node, secrets) -> bool:
    if type(node) is dict:
        for key, value in node.items():
            if type(key) is str and key in _FORBIDDEN_SECRET_KEYS:
                return True
            if _payload_contains_residual_secret(value, secrets):
                return True
        return False
    if type(node) is list:
        for item in node:
            if _payload_contains_residual_secret(item, secrets):
                return True
        return False
    if type(node) is str:
        for secret in secrets:
            if secret in node:
                return True
    return False


class KbOpenApiLiveBrokerTransport:
    def __init__(
        self,
        http_post,
        clock,
        ip_addr: str,
        mac_addr: str,
        base_url: str = DEFAULT_BASE_URL,
        excg_mktpr_ccd: str = "",
        http_timeout_seconds: int = 10,
    ):
        if not callable(http_post):
            raise ValueError("http_post must be callable")
        if not callable(clock):
            raise ValueError("clock must be callable")
        if type(ip_addr) is not str or ip_addr.strip() == "":
            raise ValueError("ip_addr must be a nonblank str")
        if type(mac_addr) is not str or mac_addr.strip() == "":
            raise ValueError("mac_addr must be a nonblank str")
        if type(base_url) is not str or not base_url.startswith(
            "https://"
        ):
            raise ValueError("base_url must be an https:// str")
        if (
            type(excg_mktpr_ccd) is not str
            or excg_mktpr_ccd not in _ALLOWED_EXCG_MKTPR_CCD
        ):
            raise ValueError("excg_mktpr_ccd is not allowed")
        if type(http_timeout_seconds) is not int:
            raise ValueError(
                "http_timeout_seconds must be a positive int"
            )
        if http_timeout_seconds <= 0:
            raise ValueError(
                "http_timeout_seconds must be a positive int"
            )
        self._http_post = http_post
        self._clock = clock
        self._ip_addr = ip_addr
        self._mac_addr = mac_addr
        self._base_url = base_url
        self._excg_mktpr_ccd = excg_mktpr_ccd
        self._http_timeout_seconds = http_timeout_seconds
        self._access_token = None
        self._token_type = None
        self._expires_at = None

    def __repr__(self) -> str:
        return (
            "KbOpenApiLiveBrokerTransport("
            f"base_url={self._base_url!r})"
        )

    def read(
        self,
        binding: ExplicitBrokerAdapterBinding,
        credential: str,
        request: ExplicitBrokerCollectRequest,
    ) -> ExplicitTransportSuccess | ExplicitTransportFailure:
        material = decode_kb_openapi_client_material(credential)
        if material is None:
            return _auth_failure()
        app_key, app_secret = material
        request_kind = getattr(request, "request_kind", None)
        if request_kind == "holdings":
            try:
                return self._read_holdings(app_key, app_secret)
            except Exception:
                return _transport_failure()
        if request_kind == "balances":
            try:
                return self._read_balances(app_key, app_secret)
            except Exception:
                return _transport_failure()
        if request_kind == "quote":
            try:
                return self._read_quote(app_key, app_secret, request)
            except Exception:
                return _transport_failure()
        if request_kind == "cash_orderability":
            try:
                return self._read_cash_orderability(app_key, app_secret)
            except Exception:
                return _transport_failure()
        if request_kind == "sell_orderability":
            try:
                return self._read_sell_orderability(app_key, app_secret, request)
            except Exception:
                return _transport_failure()
        if request_kind == "order_status":
            try:
                return self._read_order_status(app_key, app_secret, request)
            except Exception:
                return _transport_failure()
        return _validation_failure()

    def probe(
        self,
        binding: ExplicitBrokerAdapterBinding,
    ) -> ExplicitHealthProbe | ExplicitTransportFailure:
        return ExplicitHealthProbe("available", None)

    def _now(self) -> datetime:
        observed = self._clock()
        if type(observed) is not datetime:
            raise TypeError("clock must return datetime")
        if observed.tzinfo is not timezone.utc:
            raise ValueError(
                "clock tzinfo must be datetime.timezone.utc"
            )
        return observed

    def _invalidate_token(self) -> None:
        self._access_token = None
        self._token_type = None
        self._expires_at = None

    def _cached_token(self):
        if type(self._access_token) is not str:
            return None
        if self._access_token == "":
            return None
        if self._expires_at is None:
            return None
        if self._now() < self._expires_at:
            return self._access_token
        return None

    def _oauth_body(self, app_key: str, app_secret: str) -> bytes:
        return _serialize_compact_json(
            {
                "dataHeader": {
                    "ipAddr": self._ip_addr,
                    "macAddr": self._mac_addr,
                },
                "dataBody": {
                    "appKey": app_key,
                    "appSecret": app_secret,
                    "grantType": "client_credentials",
                },
            }
        )

    def _ssqm2952_body(self) -> bytes:
        return _serialize_compact_json(
            {
                "dataHeader": {
                    "ipAddr": self._ip_addr,
                    "macAddr": self._mac_addr,
                },
                "dataBody": {
                    "excg_mktpr_ccd": self._excg_mktpr_ccd,
                },
            }
        )

    def _ssqm0004_body(self) -> bytes:
        return _serialize_compact_json(
            {
                "dataHeader": {
                    "ipAddr": self._ip_addr,
                    "macAddr": self._mac_addr,
                },
                "dataBody": {
                    "is_no": "",
                },
            }
        )

    def _post(self, url: str, headers: dict, body: bytes):
        return self._http_post(
            url,
            headers,
            body,
            self._http_timeout_seconds,
        )

    def _issue_token(self, app_key: str, app_secret: str):
        response = self._post(
            self._base_url + "/oauth2/token",
            {"Content-Type": "application/json"},
            self._oauth_body(app_key, app_secret),
        )
        if type(response) is not KbOpenApiHttpResponse:
            return _transport_failure()
        if type(response.status_code) is not int:
            return _transport_failure()
        if type(response.body_text) is not str:
            return _transport_failure()
        if response.status_code == 429:
            return _rate_limited()
        if response.status_code != 200:
            return _auth_failure()
        try:
            parsed = json.loads(response.body_text)
        except ValueError:
            return _auth_failure()
        if type(parsed) is not dict:
            return _auth_failure()
        header = parsed.get("dataHeader")
        body = parsed.get("dataBody")
        if type(header) is not dict or type(body) is not dict:
            return _auth_failure()
        if header.get("processFlag") != "A":
            return _auth_failure()
        access_token = body.get("access_token")
        token_type = body.get("token_type")
        if type(access_token) is not str or access_token == "":
            return _auth_failure()
        if token_type != "Bearer":
            return _auth_failure()
        expires_in = body.get("expires_in")
        if (
            type(expires_in) is int
            and expires_in > TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS
        ):
            issued_at = self._now()
            self._access_token = access_token
            self._token_type = token_type
            self._expires_at = issued_at + timedelta(
                seconds=(
                    expires_in - TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS
                )
            )
        return access_token

    def _obtain_token(self, app_key: str, app_secret: str):
        cached = self._cached_token()
        if cached is not None:
            return cached
        return self._issue_token(app_key, app_secret)

    def _post_ssqm2952(self, access_token: str):
        response = self._post(
            self._base_url + "/api/v1/ssqm2952",
            {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + access_token,
            },
            self._ssqm2952_body(),
        )
        if type(response) is not KbOpenApiHttpResponse:
            return _transport_failure()
        if type(response.status_code) is not int:
            return _transport_failure()
        if type(response.body_text) is not str:
            return _transport_failure()
        if response.status_code == 401:
            return _UNAUTHORIZED
        if response.status_code == 429:
            return _rate_limited()
        if response.status_code != 200:
            return _provider_error()
        try:
            parsed = json.loads(response.body_text)
        except ValueError:
            return _validation_failure()
        if type(parsed) is not dict:
            return _validation_failure()
        header = parsed.get("dataHeader")
        if type(header) is not dict:
            return _validation_failure()
        if "processFlag" not in header:
            return _validation_failure()
        if header["processFlag"] != "A":
            return _provider_error()
        body = parsed.get("dataBody")
        if type(body) is not dict:
            return _validation_failure()
        return ExplicitTransportSuccess(parsed)

    def _read_holdings(self, app_key: str, app_secret: str):
        token = self._obtain_token(app_key, app_secret)
        if type(token) is ExplicitTransportFailure:
            return token
        result = self._post_ssqm2952(token)
        if result is _UNAUTHORIZED:
            self._invalidate_token()
            token = self._obtain_token(app_key, app_secret)
            if type(token) is ExplicitTransportFailure:
                return token
            result = self._post_ssqm2952(token)
            if result is _UNAUTHORIZED:
                return _auth_failure()
        if type(result) is not ExplicitTransportSuccess:
            return result
        secrets = _residual_secret_values(app_key, app_secret, token)
        if _payload_contains_residual_secret(result.body, secrets):
            return _validation_failure()
        return result

    def _post_ssqm0004(self, access_token: str):
        response = self._post(
            self._base_url + "/api/v1/ssqm0004",
            {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + access_token,
            },
            self._ssqm0004_body(),
        )
        if type(response) is not KbOpenApiHttpResponse:
            return _transport_failure()
        if type(response.status_code) is not int:
            return _transport_failure()
        if type(response.body_text) is not str:
            return _transport_failure()
        if response.status_code == 401:
            return _UNAUTHORIZED
        if response.status_code == 429:
            return _rate_limited()
        if response.status_code != 200:
            return _provider_error()
        try:
            parsed = json.loads(response.body_text)
        except ValueError:
            return _validation_failure()
        if type(parsed) is not dict:
            return _validation_failure()
        header = parsed.get("dataHeader")
        if type(header) is not dict:
            return _validation_failure()
        if "processFlag" not in header:
            return _validation_failure()
        if header["processFlag"] != "A":
            return _provider_error()
        body = parsed.get("dataBody")
        if type(body) is not dict:
            return _validation_failure()
        return ExplicitTransportSuccess(parsed)

    def _read_balances(self, app_key: str, app_secret: str):
        token = self._obtain_token(app_key, app_secret)
        if type(token) is ExplicitTransportFailure:
            return token
        result = self._post_ssqm0004(token)
        if result is _UNAUTHORIZED:
            self._invalidate_token()
            token = self._obtain_token(app_key, app_secret)
            if type(token) is ExplicitTransportFailure:
                return token
            result = self._post_ssqm0004(token)
            if result is _UNAUTHORIZED:
                return _auth_failure()
        if type(result) is not ExplicitTransportSuccess:
            return result
        secrets = _residual_secret_values(app_key, app_secret, token)
        if _payload_contains_residual_secret(result.body, secrets):
            return _validation_failure()
        return result

    def _ivu10140_body(self, shrt_cd: str) -> bytes:
        return _serialize_compact_json(
            {
                "dataHeader": {
                    "ipAddr": self._ip_addr,
                    "macAddr": self._mac_addr,
                },
                "dataBody": {
                    "excg_clsf": "0",
                    "shrt_cd": shrt_cd,
                },
            }
        )

    def _ssqm1802_body(self) -> bytes:
        return _serialize_compact_json(
            {
                "dataHeader": {
                    "ipAddr": self._ip_addr,
                    "macAddr": self._mac_addr,
                },
                "dataBody": {
                    "bnd_mktio_ccd": "1",
                    "is_no": "",
                },
            }
        )

    def _ssqm1801_body(self, is_no: str) -> bytes:
        return _serialize_compact_json(
            {
                "dataHeader": {
                    "ipAddr": self._ip_addr,
                    "macAddr": self._mac_addr,
                },
                "dataBody": {
                    "mkt_tm_ccd": "1",
                    "act_cd": "",
                    "nxt_key": "",
                    "spclz_ordr_ccd": "",
                    "inq_clsf": "0",
                    "is_no": is_no,
                },
            }
        )

    def _ssqm2341_body(self, order_date: str, order_no: str) -> bytes:
        return _serialize_compact_json(
            {
                "dataHeader": {
                    "ipAddr": self._ip_addr,
                    "macAddr": self._mac_addr,
                },
                "dataBody": {
                    "b_ccls_amt": "",
                    "ccls_clsf": "0",
                    "nxt_key": "",
                    "s_ccls_q": "",
                    "is_nm": "",
                    "inq_clsf": "9",
                    "is_cd": "",
                    "ordr_dt": order_date,
                    "orgn_ordr_no": "",
                    "b_ccls_q": "",
                    "s_ccls_amt": "",
                    "mthr_ordr_no": "",
                    "cn_clsf": "",
                    "ac_nm": "",
                    "ordr_no": order_no,
                },
            }
        )

    def _post_read_api(self, access_token: str, path: str, body: bytes):
        response = self._post(
            self._base_url + path,
            {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + access_token,
            },
            body,
        )
        if type(response) is not KbOpenApiHttpResponse:
            return _transport_failure()
        if type(response.status_code) is not int:
            return _transport_failure()
        if type(response.body_text) is not str:
            return _transport_failure()
        if response.status_code == 401:
            return _UNAUTHORIZED
        if response.status_code == 429:
            return _rate_limited()
        if response.status_code != 200:
            return _provider_error()
        try:
            parsed = json.loads(response.body_text)
        except ValueError:
            return _validation_failure()
        if type(parsed) is not dict:
            return _validation_failure()
        header = parsed.get("dataHeader")
        if type(header) is not dict:
            return _validation_failure()
        if "processFlag" not in header:
            return _validation_failure()
        if header["processFlag"] != "A":
            return _provider_error()
        body_obj = parsed.get("dataBody")
        if type(body_obj) is not dict:
            return _validation_failure()
        return ExplicitTransportSuccess(parsed)

    def _read_with_token(self, app_key, app_secret, post_fn):
        token = self._obtain_token(app_key, app_secret)
        if type(token) is ExplicitTransportFailure:
            return token
        result = post_fn(token)
        if result is _UNAUTHORIZED:
            self._invalidate_token()
            token = self._obtain_token(app_key, app_secret)
            if type(token) is ExplicitTransportFailure:
                return token
            result = post_fn(token)
            if result is _UNAUTHORIZED:
                return _auth_failure()
        if type(result) is not ExplicitTransportSuccess:
            return result
        secrets = _residual_secret_values(app_key, app_secret, token)
        if _payload_contains_residual_secret(result.body, secrets):
            return _validation_failure()
        return result

    def _read_quote(self, app_key, app_secret, request):
        params = getattr(request, "read_parameters", None)
        if params is None or type(params.instrument_code) is not str:
            return _validation_failure()
        shrt_cd = params.instrument_code.strip()
        if shrt_cd == "":
            return _validation_failure()
        body = self._ivu10140_body(shrt_cd)
        return self._read_with_token(
            app_key,
            app_secret,
            lambda token: self._post_read_api(token, "/api/v1/ivu10140", body),
        )

    def _read_cash_orderability(self, app_key, app_secret):
        body = self._ssqm1802_body()
        return self._read_with_token(
            app_key,
            app_secret,
            lambda token: self._post_read_api(token, "/api/v1/ssqm1802", body),
        )

    def _read_sell_orderability(self, app_key, app_secret, request):
        params = getattr(request, "read_parameters", None)
        is_no = ""
        if params is not None and type(params.instrument_code) is str:
            is_no = params.instrument_code.strip()
        body = self._ssqm1801_body(is_no)
        return self._read_with_token(
            app_key,
            app_secret,
            lambda token: self._post_read_api(token, "/api/v1/ssqm1801", body),
        )

    def _post_ssqm2341_status(self, access_token: str, body: bytes):
        """Status READ tolerates processFlag A or B so recovery can classify."""
        response = self._post(
            self._base_url + "/api/v1/ssqm2341",
            {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + access_token,
            },
            body,
        )
        if type(response) is not KbOpenApiHttpResponse:
            return _transport_failure()
        if type(response.status_code) is not int:
            return _transport_failure()
        if type(response.body_text) is not str:
            return _transport_failure()
        if response.status_code == 401:
            return _UNAUTHORIZED
        if response.status_code == 429:
            return _rate_limited()
        if response.status_code != 200:
            return _provider_error()
        try:
            parsed = json.loads(response.body_text)
        except ValueError:
            return _validation_failure()
        if type(parsed) is not dict:
            return _validation_failure()
        header = parsed.get("dataHeader")
        if type(header) is not dict:
            return _validation_failure()
        if "processFlag" not in header:
            return _validation_failure()
        if header["processFlag"] not in ("A", "B"):
            return _provider_error()
        body_obj = parsed.get("dataBody")
        if type(body_obj) is not dict:
            return _validation_failure()
        return ExplicitTransportSuccess(parsed)

    def _read_order_status(self, app_key, app_secret, request):
        params = getattr(request, "read_parameters", None)
        order_date = ""
        order_no = ""
        if params is not None:
            if type(params.order_date) is str:
                order_date = params.order_date.strip()
            if type(params.order_no) is str:
                order_no = params.order_no.strip()
        body = self._ssqm2341_body(order_date, order_no)
        return self._read_with_token(
            app_key,
            app_secret,
            lambda token: self._post_ssqm2341_status(token, body),
        )
