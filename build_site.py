#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path("/workspace/agp")
DASH = Path("/workspace/agp/dashboard")

def fmt(v, pct=False):
    if v is None:
        return "—"
    if isinstance(v, str):
        return v
    if pct and isinstance(v, (int, float)) and v <= 1.5:
        return f"{100 * v:.1f}%"
    if isinstance(v, float):
        return f"{v:.3f}".rstrip("0").rstrip(".")
    return str(v)

def delta(a, b, pct=False, invert=False):
    if a is None or b is None:
        return "—", "flat"
    try:
        a, b = float(a), float(b)
    except Exception:
        return "—", "flat"
    d = b - a
    if abs(d) < 1e-9:
        return "0", "flat"
    better = (d > 0 and not invert) or (d < 0 and invert)
    trend = "up" if d > 0 else "down"
    tone = "good" if better else "bad"
    if pct and abs(a) <= 1.5 and abs(b) <= 1.5:
        label = f"{100 * d:+.1f} pp"
    else:
        label = f"{d:+.3f}".rstrip("0").rstrip(".")
    return label, f"{trend}-{tone}"

def rebuild_html(snap: dict) -> None:
    tpl_path = DASH / "template.html"
    if not tpl_path.exists():
        raise SystemExit("template.html missing")
    rows_html = []
    for r in snap["rows"]:
        tc = r.get("trend") or "flat"
        short = tc.split("-")[0]
        if r.get("status") == "paused":
            cur_html = '<span class="pill paused">paused</span>'
        else:
            cur_html = f'<span class="val">{r["current"]}</span>'
        note = f'<div class="note">{r["note"]}</div>' if r.get("note") else ""
        rows_html.append(
            "<tr>"
            f'<td class="kpi-name">{r["label"]}{note}</td>'
            f'<td class="num">{r["baseline"]}</td>'
            f'<td class="num cur">{cur_html}</td>'
            f'<td class="num delta {tc}">{r["delta"]}</td>'
            f'<td><span class="trend {tc}">{short}</span></td>'
            f'<td><span class="src">{r["source"]}</span></td>'
            "</tr>"
        )
    axes_html = []
    for a in snap["axes"]:
        axes_html.append(
            '<div class="axis-card">'
            f'<div class="axis-label">{a["label"]}</div>'
            f'<div class="axis-value">{a["value"]}</div>'
            f'<div class="axis-meta"><span class="src">{a["source"]}</span> · {a["detail"]}</div>'
            "</div>"
        )
    gallery = []
    for e in snap["evidence"]:
        if e["kind"] == "video":
            gallery.append(
                f'<figure class="media-card video"><video src="{e["src"]}" controls playsinline muted loop preload="metadata" poster="assets/dashboard.png"></video><figcaption>{e["name"]}</figcaption></figure>'
            )
        else:
            gallery.append(
                f'<figure class="media-card"><a href="{e["src"]}" target="_blank" rel="noopener"><img src="{e["src"]}" alt="{e["name"]}" loading="lazy" /></a><figcaption>{e["name"]}</figcaption></figure>'
            )
    html = (
        tpl_path.read_text()
        .replace("{{ROWS}}", "".join(rows_html))
        .replace("{{AXES}}", "".join(axes_html))
        .replace("{{GALLERY}}", "".join(gallery))
        .replace("{{CYCLE}}", str(snap.get("cycle")))
        .replace("{{DECISION}}", str(snap.get("decision") or "—"))
        .replace("{{MODE}}", str(snap.get("mode")))
        .replace("{{UPDATED}}", str(snap.get("generated_at")))
        .replace("{{HIST_JSON}}", json.dumps(snap["history"]))
    )
    (DASH / "index.html").write_text(html)

def main():
    hist = []
    hp = ROOT / "v4" / "METRICS_HISTORY.jsonl"
    if hp.exists():
        for line in hp.read_text().splitlines():
            if line.strip():
                hist.append(json.loads(line))
    baseline = next((h for h in hist if h.get("cycle") == 0), hist[0] if hist else {})
    current = hist[-1] if hist else {}
    bk = (baseline or {}).get("kpi") or {}
    ck = (current or {}).get("kpi") or {}
    bs = (baseline or {}).get("source") or {}
    cs = (current or {}).get("source") or {}
    kpi_defs = [
        ("win_rate", "Win rate", True, "Never mix LIVE with SIM/LOG practice WR"),
        ("spell_hit", "Spell hit rate", True, None),
        ("elixir_waste_s", "Elixir waste (s)", False, None),
        ("threat_coverage", "Meta/ladder threat coverage", True, None),
        ("counter_success_strict", "Counter success (strict)", True, None),
        ("deck_upgrades_day", "Deck upgrades / day", False, None),
        ("claim_rate", "Reward claim rate", True, None),
        ("pro_plays", "Pro plays learned", False, None),
        ("own_matches", "Own-match sample", False, None),
        ("decision_match", "Decision-match vs pros", True, None),
        ("bc_within1", "Imitation placement accuracy", True, None),
        ("placement_heatmap_sim", "Placement accuracy (SIM)", True, None),
        ("deck_meta_alignment", "Deck building vs meta", True, None),
    ]
    rows = []
    for key, label, pct, note in kpi_defs:
        bv, cv = bk.get(key), ck.get(key)
        dlabel, trend = delta(bv, cv, pct=pct, invert=(key == "elixir_waste_s"))
        src = cs.get(key) or bs.get(key) or "—"
        status = "paused" if key == "win_rate" and cv is None else "ok"
        rows.append({
            "key": key,
            "label": label,
            "baseline": fmt(bv, pct),
            "current": "paused" if status == "paused" else fmt(cv, pct),
            "delta": dlabel,
            "trend": trend,
            "source": "LIVE" if status == "paused" else src,
            "note": note,
            "status": status,
        })
    axes = [
        {"label": "Placement accuracy", "value": fmt(ck.get("placement_heatmap_sim"), True), "source": cs.get("placement_heatmap_sim", "SIM"), "detail": "SIM heatmap / VOD overlays"},
        {"label": "Deck building vs meta", "value": fmt(ck.get("deck_meta_alignment"), True), "source": cs.get("deck_meta_alignment", "LOG+WEB"), "detail": "Alignment to seen-opponent / meta plans"},
        {"label": "Counters", "value": fmt(ck.get("counter_success_strict"), True), "source": cs.get("counter_success_strict", "LOG"), "detail": "Strict counter success"},
        {"label": "Spell aim", "value": fmt(ck.get("spell_hit"), True), "source": cs.get("spell_hit", "SIM"), "detail": "Spell impact audit / SIM casts"},
        {"label": "Movement / elixir", "value": fmt(ck.get("elixir_waste_s"), False), "source": cs.get("elixir_waste_s", "SIM"), "detail": "Seconds elixir wasted (lower better)"},
        {"label": "Upgrades / rewards", "value": "paused", "source": "LIVE", "detail": "LIVE paused until James greenlights play"},
    ]
    evidence = json.loads((DASH / "assets" / "evidence.json").read_text()) if (DASH / "assets" / "evidence.json").exists() else []
    hist_points = []
    for h in hist:
        k = h.get("kpi") or {}
        hist_points.append({
            "cycle": h.get("cycle"),
            "spell_hit": k.get("spell_hit"),
            "counter": k.get("counter_success_strict"),
            "placement": k.get("placement_heatmap_sim"),
            "decision": k.get("decision_match"),
            "elixir": k.get("elixir_waste_s"),
            "decision_tag": h.get("decision"),
        })
    out = {
        "product": "AI Game Player",
        "tagline": "Progress you can watch — the AI's climb, with receipts.",
        "generated_at": current.get("ts") or "2026-11-01",
        "mode": current.get("mode") or "offline",
        "cycle": current.get("cycle"),
        "decision": current.get("decision"),
        "change": current.get("change"),
        "live_status": "paused",
        "baseline_cycle": baseline.get("cycle", 0),
        "rows": rows,
        "axes": axes,
        "history": hist_points,
        "evidence": evidence,
    }
    (DASH / "assets" / "snapshot.json").write_text(json.dumps(out, indent=2))
    rebuild_html(out)
    print("OK", DASH / "index.html")

if __name__ == "__main__":
    main()
