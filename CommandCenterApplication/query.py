"""Strict read-only SQLite queries for the application boundary."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from FactStore.models import ExplicitStoredFactRecord
from FactStore.validation.validators import (
    validate_explicit_stored_fact_record,
    verify_stored_fact_integrity,
)
from InvestmentDecisionVerticalSlice.models import JournalRecordKind
from OperationalCioCycle.codec import decode
from CommandCenterReadOnlyOperation.models import ReadOnlyObservation
from CommandCenterReadOnlyOperation.validation import validate_read_only_observation

from CommandCenterApplication.models import (
    ApplicationDataset,
    JournalArtifact,
    MODE_REAL_READ_ONLY,
)


def _existing_file(path, label: str) -> Path:
    if not isinstance(path, (str, Path)):
        raise TypeError(f"{label} path required")
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file():
        raise ValueError(f"{label} database must already exist")
    return resolved


def _read_only_connection(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.execute("PRAGMA query_only = ON")
    return connection


def read_verified_facts(path) -> tuple[ExplicitStoredFactRecord, ...]:
    database = _existing_file(path, "FactStore")
    connection = _read_only_connection(database)
    try:
        rows = connection.execute(
            "SELECT fact_id,envelope_id,provider_id,source_class,collected_at,"
            "appended_at,status,payload_json,superseded_fact_id,integrity_seal "
            "FROM fact_records ORDER BY append_sequence"
        ).fetchall()
    except sqlite3.Error as exc:
        raise ValueError("FactStore read-only query failed") from exc
    finally:
        connection.close()
    records = []
    seen = set()
    successors = set()
    for row in rows:
        try:
            record = ExplicitStoredFactRecord(
                row[0], row[1], row[2], row[3], datetime.fromisoformat(row[4]),
                datetime.fromisoformat(row[5]), row[6], json.loads(row[7]), row[8], row[9],
            )
            validate_explicit_stored_fact_record(record)
            verify_stored_fact_integrity(record)
        except Exception as exc:
            raise ValueError("FactStore integrity verification failed") from exc
        predecessor = record.superseded_fact_id
        if predecessor is not None:
            if predecessor not in seen or predecessor in successors:
                raise ValueError("FactStore supersession history invalid")
            successors.add(predecessor)
        seen.add(record.fact_id)
        records.append(record)
    return tuple(records)


def _journal_seal(record_id, kind, created_at, payload_json, previous):
    return hashlib.sha256(
        "\n".join((record_id, kind, created_at, payload_json, previous)).encode()
    ).hexdigest()


def _canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _decode_record_artifacts(record_id, kind, created_at, payload) -> tuple[JournalArtifact, ...]:
    encoded = []
    if set(payload) == {"version", "source_event_id", "artifact"} and payload["version"] == 1:
        encoded.append(payload["artifact"])
    elif kind == JournalRecordKind.OPERATIONAL_CIO_CYCLE.value:
        if payload.get("version") != 1:
            raise ValueError("unsupported operational cycle journal version")
        for key in ("result", "artifacts"):
            if key in payload:
                encoded.append(payload[key])
    artifacts = []
    for item in encoded:
        try:
            artifact = decode(item)
        except Exception as exc:
            raise ValueError("decision artifact decode failed") from exc
        artifacts.append(JournalArtifact(record_id, kind, created_at, artifact))
    return tuple(artifacts)


def read_verified_journal(path) -> tuple[tuple[JournalArtifact, ...], int]:
    database = _existing_file(path, "DecisionJournal")
    connection = _read_only_connection(database)
    try:
        rows = connection.execute(
            "SELECT record_id,kind,created_at,payload_json,previous_seal,integrity_seal "
            "FROM decision_records ORDER BY sequence"
        ).fetchall()
    except sqlite3.Error as exc:
        raise ValueError("DecisionJournal read-only query failed") from exc
    finally:
        connection.close()
    previous = ""
    artifacts = []
    for row in rows:
        try:
            payload = json.loads(row[3])
            created_at = datetime.fromisoformat(row[2])
            JournalRecordKind(row[1])
        except Exception as exc:
            raise ValueError("DecisionJournal decode failed") from exc
        canonical = _canonical(payload)
        if row[4] != previous or row[5] != _journal_seal(row[0], row[1], row[2], canonical, row[4]):
            raise ValueError("DecisionJournal integrity chain mismatch")
        artifacts.extend(_decode_record_artifacts(row[0], row[1], created_at, payload))
        previous = row[5]
    return tuple(artifacts), len(rows)


def load_real_read_only_dataset(*, fact_store_path, journal_path, now) -> ApplicationDataset:
    if type(now) is not datetime or now.tzinfo is not timezone.utc:
        raise ValueError("now must be UTC")
    facts = read_verified_facts(fact_store_path)
    artifacts, count = read_verified_journal(journal_path)
    observations = tuple(
        item.artifact for item in artifacts
        if type(item.artifact) is ReadOnlyObservation
    )
    change_class = None
    phase7_facts = any(
        x.fact_id.startswith((
            "raw-fact:", "fact-position:", "fact-position-value:",
        ))
        for x in facts
    )
    if phase7_facts and not observations:
        raise ValueError("Phase 7 facts have no published observation")
    if observations:
        observation = max(observations, key=lambda x: x.created_at)
        validate_read_only_observation(observation)
        by_id = {x.fact_id: x for x in facts}
        missing = set(observation.application_fact_ids) - set(by_id)
        if missing:
            raise ValueError("read-only observation references missing facts")
        facts = tuple(by_id[x] for x in observation.application_fact_ids)
        change_class = observation.change_class
    return ApplicationDataset(
        MODE_REAL_READ_ONLY,
        "Verified local FactStore + DecisionJournal (read-only)",
        now,
        facts,
        artifacts,
        count,
        change_class,
    )
