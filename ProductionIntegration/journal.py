"""Closed DecisionJournal adapter for Block E; no runner/config/secrets persisted."""
from __future__ import annotations

import re
from datetime import datetime, timezone

from CommandCenterRuntime.attention import seal_human_attention_item
from CommandCenterRuntime.checkpoint import seal_operational_checkpoint
from CommandCenterRuntime.idempotency import seal_idempotency_record
from CommandCenterRuntime.integrity import integrity_seal
from CommandCenterRuntime.models import CommandCenterReport, HumanAttentionItem, IdempotencyRecord, OperationalCheckpoint, WakeEvent
from CommandCenterRuntime.wake import verify_wake_event
from InvestmentDecisionVerticalSlice.models import JournalAppend, JournalRecordKind
from InvestmentDecisionVerticalSlice.sqlite_journal import DecisionJournal
from OperationalCioCycle.codec import decode, encode


_SECRET_VALUE = re.compile(
    r"(?i)(bearer\s+[a-z0-9._-]+|(?:app.?key|app.?secret|access.?token|api.?key|"
    r"token|authorization|password|secret|credential|private.?key)\s*[:=]\s*\S+)"
)
_SECRET_KEYS = frozenset({
    "appkey", "appsecret", "accesstoken", "token", "bearer", "authorization",
    "password", "secret", "credential", "apikey", "privatekey",
})


def _normalized_key(value):
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())


def _assert_no_secret(value):
    if type(value) is str and _SECRET_VALUE.search(value):
        raise ValueError("credential material forbidden in durable journal")
    if type(value) is dict:
        for key, item in value.items():
            if _normalized_key(key) in _SECRET_KEYS:
                raise ValueError("credential material forbidden in durable journal")
            _assert_no_secret(item)
    elif type(value) in (tuple, list):
        for item in value:
            _assert_no_secret(item)


class ProductionJournal:
    def __init__(self, journal: DecisionJournal):
        if type(journal) is not DecisionJournal:
            raise TypeError("existing DecisionJournal required")
        self.journal = journal

    def append_artifact(self, kind, record_id, artifact, created_at, source_event_id):
        return self.append_artifacts(((kind, record_id, artifact),), created_at, source_event_id)[0]

    def append_artifacts(self, artifacts, created_at, source_event_id):
        if type(artifacts) is not tuple or not artifacts:
            raise ValueError("nonempty artifact tuple required")
        if type(created_at) is not datetime or created_at.tzinfo is not timezone.utc:
            raise ValueError("created_at must be UTC")
        batch = []
        returned = []
        records = self.journal.list_records()
        by_id = {x.record_id: x for x in records}
        for kind, record_id, artifact in artifacts:
            if type(kind) is not JournalRecordKind:
                raise TypeError("JournalRecordKind required")
            payload = {"version": 1, "source_event_id": source_event_id, "artifact": encode(artifact)}
            _assert_no_secret(payload)
            existing = by_id.get(record_id)
            if existing is not None:
                if existing.kind is not kind or existing.payload != payload:
                    raise ValueError("durable artifact identity collision")
                returned.append(existing)
                continue
            batch.append(JournalAppend(record_id, kind, created_at, payload))
        if batch:
            stored = self.journal.append_batch(tuple(batch))
            returned.extend(stored)
        return tuple(returned)

    def load(self, kind, record_id=None):
        results = []
        for record in self.journal.list_records():
            if record.kind is not kind or (record_id is not None and record.record_id != record_id):
                continue
            if set(record.payload) != {"version", "source_event_id", "artifact"} or record.payload["version"] != 1:
                raise ValueError("production journal payload schema mismatch")
            artifact = decode(record.payload["artifact"])
            results.append((record, artifact))
        return tuple(results)

    def contains_exact(self, kind, record_id, artifact):
        loaded = self.load(kind, record_id)
        return len(loaded) == 1 and loaded[0][1] == artifact

    def append_command_center(self, result, idempotency_records, source_event_id, now):
        batch = []
        artifacts = []
        artifacts.extend((JournalRecordKind.WAKE_EVENT, x.wake_event_id, x) for x in result.wake_events)
        if result.checkpoint is not None:
            artifacts.append((JournalRecordKind.OPERATIONAL_CHECKPOINT,
                result.checkpoint.checkpoint_id + ":" + result.checkpoint.integrity_seal, result.checkpoint))
        artifacts.extend((JournalRecordKind.HUMAN_ATTENTION_ITEM, x.attention_id, x) for x in result.attention_items)
        if result.report is not None:
            artifacts.append((JournalRecordKind.COMMAND_CENTER_REPORT,
                result.report.report_id + ":" + result.report.integrity_seal, result.report))
        if result.result_kind == "success":
            artifacts.extend((JournalRecordKind.COMMAND_CENTER_IDEMPOTENCY, x.idempotency_key, x) for x in idempotency_records)
        for kind, record_id, artifact in artifacts:
            payload = {"version": 1, "source_event_id": source_event_id, "artifact": encode(artifact)}
            _assert_no_secret(payload)
            existing = [x for x in self.journal.list_records() if x.record_id == record_id]
            if existing:
                same_artifact = (
                    existing[0].kind is kind
                    and set(existing[0].payload) == {"version", "source_event_id", "artifact"}
                    and existing[0].payload["version"] == 1
                    and existing[0].payload["artifact"] == payload["artifact"]
                )
                if not same_artifact:
                    raise ValueError("command center record collision")
                continue
            batch.append(JournalAppend(record_id, kind, now, payload))
        if batch:
            self.journal.append_batch(tuple(batch))

    def recovery_records(self):
        all_records = self.journal.list_records()
        wakes = tuple(x for _, x in self.load(JournalRecordKind.WAKE_EVENT))
        checkpoints = tuple(x for _, x in self.load(JournalRecordKind.OPERATIONAL_CHECKPOINT))
        attention = tuple(x for _, x in self.load(JournalRecordKind.HUMAN_ATTENTION_ITEM))
        idem = tuple(x for _, x in self.load(JournalRecordKind.COMMAND_CENTER_IDEMPOTENCY))
        if len({x.wake_event_id for x in wakes}) != len(wakes):
            raise ValueError("duplicate durable wake identity")
        for wake in wakes:
            verify_wake_event(wake)
        if any(type(x) is not OperationalCheckpoint for x in checkpoints):
            raise ValueError("checkpoint type mismatch")
        if any(type(x) is not HumanAttentionItem for x in attention):
            raise ValueError("attention type mismatch")
        if any(type(x) is not IdempotencyRecord for x in idem):
            raise ValueError("idempotency type mismatch")
        for item in checkpoints:
            rebuilt = seal_operational_checkpoint(
                checkpoint_id=item.checkpoint_id, cycle_id=item.cycle_id,
                wake_event_ids=item.wake_event_ids, stage_records=item.stage_records,
                attention_ids=item.attention_ids, created_at=item.created_at,
                detail=item.detail,
            )
            if rebuilt != item:
                raise ValueError("checkpoint integrity mismatch")
        for item in attention:
            rebuilt = seal_human_attention_item(
                attention_id=item.attention_id, category=item.category,
                wake_event_id=item.wake_event_id,
                bound_record_ids=item.bound_record_ids, subject_ids=item.subject_ids,
                created_at=item.created_at, detail=item.detail,
                unresolved=item.unresolved,
            )
            if rebuilt != item:
                raise ValueError("attention integrity mismatch")
        for item in idem:
            rebuilt = seal_idempotency_record(
                source_event_id=item.source_event_id,
                decision_kind=item.decision_kind,
                produced_record_id=item.produced_record_id,
                created_at=item.created_at,
            )
            if rebuilt != item:
                raise ValueError("idempotency integrity mismatch")
        for _record, report in self.load(JournalRecordKind.COMMAND_CENTER_REPORT):
            if type(report) is not CommandCenterReport:
                raise ValueError("report type mismatch")
            payload = {
                "report_id": report.report_id, "cycle_id": report.cycle_id,
                "what_changed": report.what_changed, "why_woke": report.why_woke,
                "impacts": report.impacts, "human_actions": report.human_actions,
                "execution_status": report.execution_status,
                "warnings": report.warnings, "created_at": report.created_at,
                "artifact_references": report.artifact_references,
            }
            if integrity_seal(payload) != report.integrity_seal:
                raise ValueError("report integrity mismatch")
            durable_ids = {record.record_id for record in all_records}
            for _name, reference in report.artifact_references:
                parent = reference.split("#", 1)[0]
                if parent not in durable_ids:
                    raise ValueError("report artifact reference is dangling")
        wake_ids = {x.wake_event_id for x in wakes}
        attention_ids = {x.attention_id for x in attention}
        for checkpoint in checkpoints:
            if not set(checkpoint.wake_event_ids).issubset(wake_ids):
                raise ValueError("checkpoint wake reference missing")
            if not set(checkpoint.attention_ids).issubset(attention_ids):
                raise ValueError("checkpoint attention reference missing")
        for item in attention:
            if item.wake_event_id not in wake_ids:
                raise ValueError("attention wake reference missing")
        checkpoint_ids = {x.cycle_id for x in checkpoints if x.status == "COMPLETE"}
        for item in idem:
            if item.decision_kind == "COMMAND_CENTER_CYCLE" and item.produced_record_id not in checkpoint_ids:
                raise ValueError("idempotency completion has no completed checkpoint")
        return wakes, checkpoints, attention, idem
