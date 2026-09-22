from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from FactStore.models.types import ExplicitStoredFactRecord
from FactStore.validation.validators import (
    validate_explicit_stored_fact_record,
    verify_stored_fact_integrity,
)


_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS fact_records (
    append_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    fact_id TEXT NOT NULL UNIQUE,
    envelope_id TEXT NOT NULL UNIQUE,
    provider_id TEXT NOT NULL,
    source_class TEXT NOT NULL,
    collected_at TEXT NOT NULL,
    appended_at TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    superseded_fact_id TEXT UNIQUE,
    integrity_seal TEXT NOT NULL,
    FOREIGN KEY (superseded_fact_id) REFERENCES fact_records(fact_id)
)
"""

_UPDATE_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS fact_records_no_update
BEFORE UPDATE ON fact_records
BEGIN
    SELECT RAISE(ABORT, 'fact records are immutable');
END
"""

_DELETE_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS fact_records_no_delete
BEFORE DELETE ON fact_records
BEGIN
    SELECT RAISE(ABORT, 'fact records are append-only');
END
"""

_SCHEMA = f"""
{_TABLE_SCHEMA};
{_UPDATE_TRIGGER};
{_DELETE_TRIGGER};
"""


class SQLiteAppendOnlyFactEngine:
    """Single-file durable append-only storage for accepted facts."""

    def __init__(self, database_path: str | Path) -> None:
        if not isinstance(database_path, (str, Path)):
            raise TypeError("database_path must be str or Path")
        path = Path(database_path)
        if str(path).strip() == "":
            raise ValueError("database_path must not be blank")
        self._connection = sqlite3.connect(
            str(path),
            isolation_level=None,
        )
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.execute("PRAGMA synchronous = FULL")
        self._connection.executescript(_SCHEMA)
        self._verify_schema_guards()
        self._load_verified_records()

    def append(self, record: ExplicitStoredFactRecord) -> None:
        self.append_batch((record,))

    def append_batch(
        self,
        records: tuple[ExplicitStoredFactRecord, ...],
    ) -> None:
        if type(records) is not tuple:
            raise TypeError("records must be tuple")
        for record in records:
            validate_explicit_stored_fact_record(record)
            verify_stored_fact_integrity(record)
        try:
            self._connection.execute("BEGIN IMMEDIATE")
            for record in records:
                self._connection.execute(
                    """
                    INSERT INTO fact_records (
                        fact_id, envelope_id, provider_id,
                        source_class, collected_at, appended_at,
                        status, payload_json, superseded_fact_id,
                        integrity_seal
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    self._record_values(record),
                )
            self._connection.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            self._connection.execute("ROLLBACK")
            raise ValueError(
                "durable fact batch violates append-only constraints"
            ) from exc
        except Exception:
            self._connection.execute("ROLLBACK")
            raise

    def get_by_fact_id(
        self,
        fact_id: str,
    ) -> ExplicitStoredFactRecord:
        row = self._connection.execute(
            """
            SELECT fact_id, envelope_id, provider_id, source_class,
                   collected_at, appended_at, status, payload_json,
                   superseded_fact_id, integrity_seal
            FROM fact_records WHERE fact_id = ?
            """,
            (fact_id,),
        ).fetchone()
        if row is None:
            raise ValueError("fact_id not found")
        return self._decode_verified_record(row)

    def contains_fact_id(self, fact_id: str) -> bool:
        return self._exists("fact_id", fact_id)

    def contains_envelope_id(self, envelope_id: str) -> bool:
        return self._exists("envelope_id", envelope_id)

    def list_in_append_order(
        self,
    ) -> tuple[ExplicitStoredFactRecord, ...]:
        self._verify_schema_guards()
        rows = self._connection.execute(
            """
            SELECT fact_id, envelope_id, provider_id, source_class,
                   collected_at, appended_at, status, payload_json,
                   superseded_fact_id, integrity_seal
            FROM fact_records ORDER BY append_sequence
            """
        ).fetchall()
        records = tuple(
            self._decode_verified_record(row) for row in rows
        )
        self._verify_history(records)
        return records

    def successor_of(self, fact_id: str) -> str | None:
        row = self._connection.execute(
            """
            SELECT fact_id FROM fact_records
            WHERE superseded_fact_id = ?
            """,
            (fact_id,),
        ).fetchone()
        if row is None:
            return None
        return row[0]

    def close(self) -> None:
        self._connection.close()

    def _exists(self, column: str, value: str) -> bool:
        if column not in ("fact_id", "envelope_id"):
            raise ValueError("unsupported identity column")
        row = self._connection.execute(
            f"SELECT 1 FROM fact_records WHERE {column} = ?",
            (value,),
        ).fetchone()
        return row is not None

    @staticmethod
    def _record_values(record: ExplicitStoredFactRecord) -> tuple:
        return (
            record.fact_id,
            record.envelope_id,
            record.provider_id,
            record.source_class,
            record.collected_at.isoformat(),
            record.appended_at.isoformat(),
            record.status,
            json.dumps(
                record.payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ),
            record.superseded_fact_id,
            record.integrity_seal,
        )

    @staticmethod
    def _decode_verified_record(row) -> ExplicitStoredFactRecord:
        try:
            payload = json.loads(row[7])
            record = ExplicitStoredFactRecord(
                row[0],
                row[1],
                row[2],
                row[3],
                datetime.fromisoformat(row[4]),
                datetime.fromisoformat(row[5]),
                row[6],
                payload,
                row[8],
                row[9],
            )
            validate_explicit_stored_fact_record(record)
            verify_stored_fact_integrity(record)
        except Exception as exc:
            raise ValueError(
                "durable fact record integrity verification failed"
            ) from exc
        return record

    def _load_verified_records(self) -> None:
        self.list_in_append_order()

    @staticmethod
    def _verify_history(
        records: tuple[ExplicitStoredFactRecord, ...],
    ) -> None:
        by_id = {}
        successors = set()
        for record in records:
            predecessor_id = record.superseded_fact_id
            if predecessor_id is not None:
                if predecessor_id not in by_id:
                    raise ValueError(
                        "durable supersession predecessor missing"
                    )
                if predecessor_id in successors:
                    raise ValueError(
                        "durable supersession successor duplicated"
                    )
                if (
                    by_id[predecessor_id].source_class
                    != record.source_class
                ):
                    raise ValueError(
                        "durable supersession source_class mismatch"
                    )
                successors.add(predecessor_id)
            by_id[record.fact_id] = record

    def _verify_schema_guards(self) -> None:
        if self._connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0] != 1:
            raise ValueError("durable foreign keys disabled")
        if self._connection.execute(
            "PRAGMA journal_mode"
        ).fetchone()[0].lower() != "wal":
            raise ValueError("durable WAL mode disabled")
        if self._connection.execute(
            "PRAGMA synchronous"
        ).fetchone()[0] != 2:
            raise ValueError("durable FULL sync disabled")
        columns = self._connection.execute(
            "PRAGMA table_info(fact_records)"
        ).fetchall()
        column_shape = tuple(
            (row[1], row[2], row[3], row[5]) for row in columns
        )
        if column_shape != (
            ("append_sequence", "INTEGER", 0, 1),
            ("fact_id", "TEXT", 1, 0),
            ("envelope_id", "TEXT", 1, 0),
            ("provider_id", "TEXT", 1, 0),
            ("source_class", "TEXT", 1, 0),
            ("collected_at", "TEXT", 1, 0),
            ("appended_at", "TEXT", 1, 0),
            ("status", "TEXT", 1, 0),
            ("payload_json", "TEXT", 1, 0),
            ("superseded_fact_id", "TEXT", 0, 0),
            ("integrity_seal", "TEXT", 1, 0),
        ):
            raise ValueError("durable fact table schema mismatch")
        table_row = self._connection.execute(
            """
            SELECT sql FROM sqlite_master
            WHERE type = 'table' AND name = 'fact_records'
            """
        ).fetchone()
        if (
            table_row is None
            or self._normalized_sql(table_row[0])
            != self._normalized_sql(_TABLE_SCHEMA)
        ):
            raise ValueError("durable fact table schema mismatch")
        unique_columns = set()
        for index in self._connection.execute(
            "PRAGMA index_list(fact_records)"
        ).fetchall():
            if index[2] != 1:
                continue
            details = self._connection.execute(
                f"PRAGMA index_info('{index[1]}')"
            ).fetchall()
            unique_columns.add(tuple(row[2] for row in details))
        if unique_columns != {
            ("fact_id",),
            ("envelope_id",),
            ("superseded_fact_id",),
        }:
            raise ValueError("durable unique constraints mismatch")
        foreign_keys = self._connection.execute(
            "PRAGMA foreign_key_list(fact_records)"
        ).fetchall()
        if len(foreign_keys) != 1 or (
            foreign_keys[0][2],
            foreign_keys[0][3],
            foreign_keys[0][4],
        ) != ("fact_records", "superseded_fact_id", "fact_id"):
            raise ValueError("durable foreign key schema mismatch")
        rows = self._connection.execute(
            """
            SELECT name, tbl_name, sql FROM sqlite_master
            WHERE type = 'trigger' AND name IN (
                'fact_records_no_update',
                'fact_records_no_delete'
            )
            """
        ).fetchall()
        actual = {
            row[0]: (row[1], self._normalized_sql(row[2]))
            for row in rows
        }
        expected = {
            "fact_records_no_update": (
                "fact_records",
                self._normalized_sql(_UPDATE_TRIGGER),
            ),
            "fact_records_no_delete": (
                "fact_records",
                self._normalized_sql(_DELETE_TRIGGER),
            ),
        }
        if actual != expected:
            raise ValueError("durable append-only guards mismatch")

    @staticmethod
    def _normalized_sql(value: str) -> str:
        return " ".join(
            value.replace("IF NOT EXISTS ", "")
            .replace(";", "")
            .split()
        )
