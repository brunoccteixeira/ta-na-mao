#!/usr/bin/env python3
"""
Audit script for Tá na Mão benefits catalog.
Validates all 299 benefits (60 fed + 50 set + 189 est) against a comprehensive checklist.

Usage:
    python scripts/audit_benefits.py
    python scripts/audit_benefits.py --json  # Output JSON report
"""

import json
import glob
import sys
import os
from pathlib import Path
from collections import Counter, defaultdict

# === CONSTANTS ===
SM_2026 = 1621
MEIO_SM = 810.50
TETO_INSS = 8475.55
BPC_THRESHOLD = 405.25
EXTREMA_POBREZA = 218

# Old SM values that should NOT appear
OLD_SM_VALUES = {1518, 759, 3036, 1412, 706, 2824, 1320, 660, 2640}

VALID_SECTORS = {
    "pescador", "agricultor", "entregador", "motorista_app",
    "catador", "mei", "domestica", "autonomo", "clt", "pcd"
}

VALID_STATUS = {"active", "suspended", "ended"}
VALID_VALUE_TYPES = {"monthly", "annual", "one_time"}
VALID_LEGAL_TYPES = {"lei", "decreto", "portaria", "constituicao", "resolucao", "lei_complementar", "medida_provisoria"}
VALID_SCOPES = {"federal", "state", "municipal", "sectoral"}

UF_CODES = {
    "ac", "al", "am", "ap", "ba", "ce", "df", "es", "go", "ma",
    "mg", "ms", "mt", "pa", "pb", "pe", "pi", "pr", "rj", "rn",
    "ro", "rr", "rs", "sc", "se", "sp", "to"
}

# Severity levels
CRITICAL = "CRITICAL"
HIGH = "HIGH"
MEDIUM = "MEDIUM"
LOW = "LOW"
INFO = "INFO"

BASE_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "data" / "benefits"


class AuditFinding:
    def __init__(self, benefit_id: str, category: str, severity: str, message: str, field: str = ""):
        self.benefit_id = benefit_id
        self.category = category
        self.severity = severity
        self.message = message
        self.field = field

    def to_dict(self):
        return {
            "benefit_id": self.benefit_id,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "field": self.field,
        }

    def __str__(self):
        return f"[{self.severity}] {self.benefit_id}: {self.message}"


def load_all_benefits():
    """Load all 299 benefits from JSON files."""
    benefits = []

    # Federal
    with open(BASE_DIR / "federal.json", encoding="utf-8") as f:
        fed = json.load(f)
    for b in fed["benefits"]:
        b["_source_file"] = "federal.json"
        benefits.append(b)

    # Sectoral
    with open(BASE_DIR / "sectoral.json", encoding="utf-8") as f:
        sec = json.load(f)
    for b in sec["benefits"]:
        b["_source_file"] = "sectoral.json"
        benefits.append(b)

    # States
    for fp in sorted(glob.glob(str(BASE_DIR / "states" / "*.json"))):
        uf = Path(fp).stem
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        for b in data["benefits"]:
            b["_source_file"] = f"states/{uf}.json"
            b["_expected_uf"] = uf
            benefits.append(b)

    return benefits


def check_schema(benefit: dict) -> list[AuditFinding]:
    """Check A: Schema validation."""
    findings = []
    bid = benefit.get("id", "UNKNOWN")

    # Required fields
    required = ["id", "name", "shortDescription", "scope", "eligibilityRules",
                 "whereToApply", "documentsRequired", "lastUpdated", "status"]
    for field in required:
        if field not in benefit or benefit[field] is None:
            findings.append(AuditFinding(bid, "schema", CRITICAL, f"Missing required field: {field}", field))
        elif isinstance(benefit[field], str) and not benefit[field].strip():
            findings.append(AuditFinding(bid, "schema", HIGH, f"Empty required field: {field}", field))

    # ID prefix check
    scope = benefit.get("scope", "")
    if scope == "federal" and not bid.startswith("federal-"):
        findings.append(AuditFinding(bid, "schema", HIGH, f"Federal benefit ID should start with 'federal-'", "id"))
    elif scope == "sectoral" and not bid.startswith("sectoral-"):
        findings.append(AuditFinding(bid, "schema", HIGH, f"Sectoral benefit ID should start with 'sectoral-'", "id"))
    elif scope == "state":
        expected_uf = benefit.get("_expected_uf", "")
        if expected_uf and not bid.startswith(f"{expected_uf}-"):
            findings.append(AuditFinding(bid, "schema", HIGH, f"State benefit ID should start with '{expected_uf}-'", "id"))

    # Scope validation
    if scope not in VALID_SCOPES:
        findings.append(AuditFinding(bid, "schema", CRITICAL, f"Invalid scope: {scope}", "scope"))

    # Sector validation (sectoral only)
    if scope == "sectoral":
        sector = benefit.get("sector", "")
        if not sector:
            findings.append(AuditFinding(bid, "schema", HIGH, "Sectoral benefit missing 'sector' field", "sector"))
        elif sector not in VALID_SECTORS:
            findings.append(AuditFinding(bid, "schema", HIGH, f"Invalid sector: {sector}", "sector"))

    # State validation (state only)
    if scope == "state":
        state = benefit.get("state", "")
        expected_uf = benefit.get("_expected_uf", "")
        if not state:
            findings.append(AuditFinding(bid, "schema", HIGH, "State benefit missing 'state' field", "state"))
        elif expected_uf and state.lower() != expected_uf.lower():
            findings.append(AuditFinding(bid, "schema", HIGH, f"State mismatch: {state} vs expected {expected_uf}", "state"))

    # Status validation
    status = benefit.get("status", "")
    if status not in VALID_STATUS:
        findings.append(AuditFinding(bid, "schema", HIGH, f"Invalid status: {status}", "status"))

    # EstimatedValue checks
    ev = benefit.get("estimatedValue", {})
    if ev:
        vtype = ev.get("type", "")
        if vtype and vtype not in VALID_VALUE_TYPES:
            findings.append(AuditFinding(bid, "schema", MEDIUM, f"Invalid value type: {vtype}", "estimatedValue.type"))
        vmin = ev.get("min", 0)
        vmax = ev.get("max", 0)
        if vmin and vmax and vmin > vmax:
            findings.append(AuditFinding(bid, "schema", HIGH, f"min ({vmin}) > max ({vmax})", "estimatedValue"))

    # Documents not empty
    docs = benefit.get("documentsRequired", [])
    if isinstance(docs, list) and len(docs) == 0:
        findings.append(AuditFinding(bid, "schema", MEDIUM, "Empty documentsRequired array", "documentsRequired"))

    return findings


def check_values(benefit: dict) -> list[AuditFinding]:
    """Check B: Monetary values."""
    findings = []
    bid = benefit.get("id", "UNKNOWN")
    ev = benefit.get("estimatedValue", {})
    if not ev:
        return findings

    vmin = ev.get("min", 0)
    vmax = ev.get("max", 0)

    for label, val in [("min", vmin), ("max", vmax)]:
        if val in OLD_SM_VALUES:
            findings.append(AuditFinding(bid, "values", HIGH, f"Old SM value detected: {label}={val}", f"estimatedValue.{label}"))

        # Teto INSS rounding
        if val == 8476:
            findings.append(AuditFinding(bid, "values", LOW, f"Teto INSS rounded: {label}=8476 (should be 8475.55)", f"estimatedValue.{label}"))

        # Meio SM rounding
        if val == 811:
            findings.append(AuditFinding(bid, "values", LOW, f"Meio SM rounded: {label}=811 (should be 810.50)", f"estimatedValue.{label}"))

    # Check description mentions "salário mínimo" but value doesn't match
    desc = ev.get("description", "")
    if desc and "salário mínimo" in desc.lower():
        if vmin and vmin not in (SM_2026, MEIO_SM, SM_2026 * 2, SM_2026 * 3):
            # Only flag if it's a suspiciously exact old value
            if vmin in OLD_SM_VALUES:
                findings.append(AuditFinding(bid, "values", HIGH, f"Description mentions SM but min={vmin} (SM 2026={SM_2026})", "estimatedValue"))

    # Check eligibility rules for old thresholds
    for rule in benefit.get("eligibilityRules", []):
        val = rule.get("value")
        if isinstance(val, (int, float)) and val in OLD_SM_VALUES:
            findings.append(AuditFinding(bid, "values", HIGH, f"Old SM value in eligibility rule: {rule.get('field')}={val}", "eligibilityRules"))

    return findings


def check_legal_basis(benefit: dict) -> list[AuditFinding]:
    """Check C: Legal basis (focus on federals, but check all)."""
    findings = []
    bid = benefit.get("id", "UNKNOWN")
    scope = benefit.get("scope", "")

    # Federal benefits MUST have legalBasis
    lb = benefit.get("legalBasis", {})
    if scope == "federal":
        if not lb or not lb.get("laws"):
            findings.append(AuditFinding(bid, "legal", HIGH, "Federal benefit missing legalBasis.laws", "legalBasis"))
        else:
            for i, law in enumerate(lb["laws"]):
                if not law.get("type"):
                    findings.append(AuditFinding(bid, "legal", MEDIUM, f"Law #{i} missing type", "legalBasis"))
                elif law["type"] not in VALID_LEGAL_TYPES:
                    findings.append(AuditFinding(bid, "legal", MEDIUM, f"Law #{i} invalid type: {law['type']}", "legalBasis"))
                if not law.get("number"):
                    findings.append(AuditFinding(bid, "legal", MEDIUM, f"Law #{i} missing number", "legalBasis"))
                if not law.get("description"):
                    findings.append(AuditFinding(bid, "legal", LOW, f"Law #{i} missing description", "legalBasis"))
                url = law.get("url", "")
                if url and url.startswith("http://"):
                    findings.append(AuditFinding(bid, "legal", MEDIUM, f"Law URL uses HTTP: {url}", "legalBasis"))

    # Check legalReference in eligibilityRules (federal should have them)
    rules = benefit.get("eligibilityRules", [])
    has_legal_ref = any(r.get("legalReference") for r in rules)
    if scope == "federal" and not has_legal_ref and rules:
        findings.append(AuditFinding(bid, "legal", MEDIUM, "No legalReference in any eligibility rule", "eligibilityRules"))

    return findings


def check_urls(benefit: dict) -> list[AuditFinding]:
    """Check D: URL validation."""
    findings = []
    bid = benefit.get("id", "UNKNOWN")

    source_url = benefit.get("sourceUrl", "")
    if not source_url:
        findings.append(AuditFinding(bid, "urls", MEDIUM, "Missing sourceUrl", "sourceUrl"))
    else:
        if source_url.startswith("http://"):
            findings.append(AuditFinding(bid, "urls", MEDIUM, f"sourceUrl uses HTTP (not HTTPS): {source_url}", "sourceUrl"))
        elif not source_url.startswith("https://"):
            findings.append(AuditFinding(bid, "urls", HIGH, f"sourceUrl doesn't start with https://: {source_url}", "sourceUrl"))

        # Check for shallow URLs (just domain, no path)
        parts = source_url.replace("https://", "").replace("http://", "").split("/")
        if len(parts) <= 1 or (len(parts) == 2 and parts[1] == ""):
            findings.append(AuditFinding(bid, "urls", LOW, f"Shallow sourceUrl (just domain): {source_url}", "sourceUrl"))

    return findings


def check_content(benefit: dict) -> list[AuditFinding]:
    """Check E: Content quality."""
    findings = []
    bid = benefit.get("id", "UNKNOWN")

    # Short description length
    desc = benefit.get("shortDescription", "")
    if len(desc) < 30:
        findings.append(AuditFinding(bid, "content", MEDIUM, f"shortDescription too short ({len(desc)} chars, min 30)", "shortDescription"))
    elif len(desc) > 200:
        findings.append(AuditFinding(bid, "content", LOW, f"shortDescription too long ({len(desc)} chars, max 200)", "shortDescription"))

    # Documents count
    docs = benefit.get("documentsRequired", [])
    if isinstance(docs, list) and 0 < len(docs) < 2:
        findings.append(AuditFinding(bid, "content", LOW, f"Only {len(docs)} document(s) required (expected 2+)", "documentsRequired"))

    # howToApply steps
    steps = benefit.get("howToApply", [])
    if isinstance(steps, list) and 0 < len(steps) < 3:
        findings.append(AuditFinding(bid, "content", LOW, f"Only {len(steps)} howToApply step(s) (expected 3+)", "howToApply"))
    elif not steps:
        findings.append(AuditFinding(bid, "content", MEDIUM, "Missing howToApply", "howToApply"))

    # Icon
    if not benefit.get("icon"):
        findings.append(AuditFinding(bid, "content", LOW, "Missing icon", "icon"))

    return findings


def check_cross_reference(benefits: list[dict]) -> list[AuditFinding]:
    """Check F: Cross-reference and duplicates."""
    findings = []

    # Duplicate IDs
    ids = [b.get("id", "") for b in benefits]
    id_counts = Counter(ids)
    for bid, count in id_counts.items():
        if count > 1:
            findings.append(AuditFinding(bid, "crossref", CRITICAL, f"Duplicate ID found {count} times", "id"))

    # Ended/suspended programs
    for b in benefits:
        bid = b.get("id", "")
        status = b.get("status", "")
        if status == "ended":
            findings.append(AuditFinding(bid, "crossref", INFO, "Program has status 'ended' — kept for user redirect", "status"))
        elif status == "suspended":
            findings.append(AuditFinding(bid, "crossref", INFO, "Program has status 'suspended'", "status"))

    return findings


def check_audit_status_orphans(benefits: list[dict]) -> list[AuditFinding]:
    """Check for orphan entries in audit-status.json."""
    findings = []
    audit_file = BASE_DIR / "audit-status.json"
    if not audit_file.exists():
        return findings

    with open(audit_file, encoding="utf-8") as f:
        audit = json.load(f)

    benefit_ids = {b.get("id") for b in benefits}
    # Include municipal IDs pattern too
    for aid in audit.get("benefits", {}):
        # Skip municipal IDs (they're not in scope)
        if any(aid.startswith(f"{uf}-") for uf in UF_CODES) or aid.startswith("federal-") or aid.startswith("sectoral-"):
            if aid not in benefit_ids:
                # Check if it's a municipal ID (has city name in it)
                is_municipal = False
                for uf in UF_CODES:
                    if aid.startswith(f"{uf}-") and not aid.startswith(f"federal-") and not aid.startswith(f"sectoral-"):
                        # State benefit IDs are like "sp-vivaleite", municipal are like "sp-saopaulo-restaurante"
                        parts = aid.split("-")
                        if len(parts) >= 3 and parts[0] in UF_CODES:
                            is_municipal = True
                            break
                if not is_municipal:
                    findings.append(AuditFinding(aid, "crossref", LOW, "Orphan entry in audit-status.json (ID not found in benefit files)", "audit-status"))

    return findings


def run_audit():
    """Run the complete audit."""
    print("=" * 70)
    print("TÁ NA MÃO — COMPREHENSIVE BENEFIT AUDIT")
    print("=" * 70)

    benefits = load_all_benefits()
    print(f"\nLoaded {len(benefits)} benefits")

    scope_counts = Counter(b.get("scope") for b in benefits)
    for scope, count in sorted(scope_counts.items()):
        print(f"  {scope}: {count}")

    all_findings: list[AuditFinding] = []

    # Run checks per benefit
    print("\nRunning checks...")
    for b in benefits:
        all_findings.extend(check_schema(b))
        all_findings.extend(check_values(b))
        all_findings.extend(check_legal_basis(b))
        all_findings.extend(check_urls(b))
        all_findings.extend(check_content(b))

    # Cross-reference checks (all at once)
    all_findings.extend(check_cross_reference(benefits))
    all_findings.extend(check_audit_status_orphans(benefits))

    # === REPORT ===
    print(f"\n{'=' * 70}")
    print(f"AUDIT RESULTS: {len(all_findings)} findings")
    print(f"{'=' * 70}")

    # Count by severity
    severity_counts = Counter(f.severity for f in all_findings)
    for sev in [CRITICAL, HIGH, MEDIUM, LOW, INFO]:
        count = severity_counts.get(sev, 0)
        if count > 0:
            print(f"  {sev}: {count}")

    # Count by category
    print(f"\nBy category:")
    cat_counts = Counter(f.category for f in all_findings)
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat}: {count}")

    # Count by scope
    print(f"\nBy scope:")
    scope_findings = defaultdict(int)
    for f in all_findings:
        bid = f.benefit_id
        if bid.startswith("federal-"):
            scope_findings["federal"] += 1
        elif bid.startswith("sectoral-"):
            scope_findings["sectoral"] += 1
        else:
            scope_findings["state"] += 1
    for scope, count in sorted(scope_findings.items()):
        print(f"  {scope}: {count}")

    # Detail: Critical and High
    critical_high = [f for f in all_findings if f.severity in (CRITICAL, HIGH)]
    if critical_high:
        print(f"\n{'=' * 70}")
        print(f"CRITICAL + HIGH FINDINGS ({len(critical_high)}):")
        print(f"{'=' * 70}")
        for f in sorted(critical_high, key=lambda x: (x.severity, x.benefit_id)):
            print(f"  {f}")

    # Detail: Medium
    medium = [f for f in all_findings if f.severity == MEDIUM]
    if medium:
        print(f"\n{'=' * 70}")
        print(f"MEDIUM FINDINGS ({len(medium)}):")
        print(f"{'=' * 70}")
        for f in sorted(medium, key=lambda x: x.benefit_id):
            print(f"  {f}")

    # Detail: Low
    low = [f for f in all_findings if f.severity == LOW]
    if low:
        print(f"\n{'=' * 70}")
        print(f"LOW FINDINGS ({len(low)}):")
        print(f"{'=' * 70}")
        for f in sorted(low, key=lambda x: x.benefit_id):
            print(f"  {f}")

    # JSON output
    if "--json" in sys.argv:
        report = {
            "total_benefits": len(benefits),
            "total_findings": len(all_findings),
            "severity_counts": dict(severity_counts),
            "category_counts": dict(cat_counts),
            "findings": [f.to_dict() for f in all_findings],
        }
        report_path = BASE_DIR / "audit-report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\nJSON report saved to: {report_path}")

    # Summary
    print(f"\n{'=' * 70}")
    print(f"SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total benefits audited: {len(benefits)}")
    print(f"  Total findings: {len(all_findings)}")
    print(f"  Critical: {severity_counts.get(CRITICAL, 0)}")
    print(f"  High: {severity_counts.get(HIGH, 0)}")
    print(f"  Medium: {severity_counts.get(MEDIUM, 0)}")
    print(f"  Low: {severity_counts.get(LOW, 0)}")
    print(f"  Info: {severity_counts.get(INFO, 0)}")

    has_blockers = severity_counts.get(CRITICAL, 0) > 0
    print(f"\n  Status: {'❌ BLOCKERS FOUND' if has_blockers else '⚠️ Issues found' if all_findings else '✅ ALL CLEAR'}")

    return all_findings


if __name__ == "__main__":
    findings = run_audit()
    sys.exit(1 if any(f.severity == CRITICAL for f in findings) else 0)
