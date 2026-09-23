from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from InvestmentDecisionVerticalSlice.models import JournalAppend, JournalRecordKind, StoredDecisionRecord


TABLE_SQL = """CREATE TABLE decision_records (
 sequence INTEGER PRIMARY KEY AUTOINCREMENT,
 record_id TEXT NOT NULL UNIQUE,
 kind TEXT NOT NULL,
 created_at TEXT NOT NULL,
 payload_json TEXT NOT NULL,
 previous_seal TEXT NOT NULL,
 integrity_seal TEXT NOT NULL
)"""
UPDATE_TRIGGER_SQL = """CREATE TRIGGER decision_records_no_update BEFORE UPDATE ON decision_records BEGIN SELECT RAISE(ABORT,'decision records are immutable'); END"""
DELETE_TRIGGER_SQL = """CREATE TRIGGER decision_records_no_delete BEFORE DELETE ON decision_records BEGIN SELECT RAISE(ABORT,'decision records are append-only'); END"""
SCHEMA = f"""
{TABLE_SQL};
{UPDATE_TRIGGER_SQL};
{DELETE_TRIGGER_SQL};
"""


def _canonical(payload):
    if type(payload) is not dict:
        raise TypeError("payload must be dict")
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _seal(record_id, kind, created_at, payload_json, previous):
    return hashlib.sha256("\n".join((record_id, kind, created_at, payload_json, previous)).encode()).hexdigest()


class DecisionJournal:
    def __init__(self, path):
        if not isinstance(path, (str, Path)):
            raise TypeError("path must be str or Path")
        self._connection = sqlite3.connect(str(path), isolation_level=None)
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        existing = self._connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='decision_records'").fetchone()
        if existing is None:
            self._connection.executescript(SCHEMA)
        self._verify_schema()
        self.list_records()

    def append_batch(self, batch):
        if type(batch) is not tuple or not batch:
            raise ValueError("batch must be nonempty tuple")
        prior = self.list_records()
        previous = "" if not prior else prior[-1].integrity_seal
        prepared = []
        ids = {x.record_id for x in prior}
        for item in batch:
            if type(item) is not JournalAppend:
                raise TypeError("item must be JournalAppend")
            if type(item.record_id) is not str or item.record_id.strip() == "" or item.record_id in ids:
                raise ValueError("record_id invalid or duplicated")
            if type(item.kind) is not JournalRecordKind:
                raise TypeError("kind must be JournalRecordKind")
            if type(item.created_at) is not datetime or item.created_at.tzinfo is not timezone.utc:
                raise ValueError("created_at must be UTC datetime")
            payload = _canonical(item.payload)
            seal = _seal(item.record_id, item.kind.value, item.created_at.isoformat(), payload, previous)
            prepared.append((item, payload, previous, seal)); previous = seal; ids.add(item.record_id)
        try:
            self._connection.execute("BEGIN IMMEDIATE")
            for item, payload, previous, seal in prepared:
                self._connection.execute("INSERT INTO decision_records(record_id,kind,created_at,payload_json,previous_seal,integrity_seal) VALUES(?,?,?,?,?,?)", (item.record_id,item.kind.value,item.created_at.isoformat(),payload,previous,seal))
            self._connection.execute("COMMIT")
        except Exception:
            self._connection.execute("ROLLBACK"); raise
        return self.list_records()[-len(batch):]

    def list_records(self):
        self._verify_schema()
        rows = self._connection.execute("SELECT sequence,record_id,kind,created_at,payload_json,previous_seal,integrity_seal FROM decision_records ORDER BY sequence").fetchall()
        records=[]; previous=""
        for row in rows:
            try:
                payload=json.loads(row[4]); created=datetime.fromisoformat(row[3]); kind=JournalRecordKind(row[2])
            except Exception as exc: raise ValueError("decision journal decode failure") from exc
            if row[5] != previous or row[6] != _seal(row[1],row[2],row[3],_canonical(payload),row[5]):
                raise ValueError("decision journal integrity chain mismatch")
            records.append(StoredDecisionRecord(row[0],row[1],kind,created,payload,row[5],row[6])); previous=row[6]
        return tuple(records)

    def close(self): self._connection.close()

    def _verify_schema(self):
        if self._connection.execute("PRAGMA journal_mode").fetchone()[0].lower() != "wal" or self._connection.execute("PRAGMA synchronous").fetchone()[0] != 2:
            raise ValueError("decision journal durability disabled")
        columns=tuple((x[1],x[2],x[3],x[5]) for x in self._connection.execute("PRAGMA table_info(decision_records)"))
        expected=(("sequence","INTEGER",0,1),("record_id","TEXT",1,0),("kind","TEXT",1,0),("created_at","TEXT",1,0),("payload_json","TEXT",1,0),("previous_seal","TEXT",1,0),("integrity_seal","TEXT",1,0))
        if columns != expected: raise ValueError("decision journal schema mismatch")
        normalize=lambda value:" ".join(value.replace(";","").split())
        table=self._connection.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='decision_records'").fetchone()
        if table is None or normalize(table[0]) != normalize(TABLE_SQL): raise ValueError("decision journal schema mismatch")
        unique={tuple(x[2] for x in self._connection.execute(f"PRAGMA index_info('{row[1]}')")) for row in self._connection.execute("PRAGMA index_list(decision_records)") if row[2] == 1}
        if unique != {("record_id",)}: raise ValueError("decision journal unique constraint mismatch")
        triggers={x[0]:" ".join(x[1].replace(";","").split()) for x in self._connection.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger'")}
        if triggers != {"decision_records_no_update":normalize(UPDATE_TRIGGER_SQL),"decision_records_no_delete":normalize(DELETE_TRIGGER_SQL)}:
            raise ValueError("decision journal mutation guards mismatch")
