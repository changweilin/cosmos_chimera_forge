#!/usr/bin/env python3
"""
Build _creature_feature_lookup_table.{json,md} and _character_feature_lookup_table.{json,md}
mirroring Drive/moves/_designed_prompts/_move_feature_lookup_table.json.

Usage:
    python tools/build_feature_lookup_tables.py
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
from pathlib import Path
from typing import Any

if __package__:
    from .project_drive import REPO_ROOT as ROOT, project_drive_root
else:
    from project_drive import REPO_ROOT as ROOT, project_drive_root

DRIVE = project_drive_root()
GAME_REPO = ROOT.parent / "cosmos_chimera"

MAX_OVERLAP_PCT = 60.0

ELEMENT_ZH = {
    "earth": "土",
    "fire": "火",
    "ice": "冰",
    "light": "光",
    "metal": "金",
    "shadow": "影",
    "thunder": "雷",
    "water": "水",
    "wind": "風",
    "wood": "木",
    "sun": "光火",
    "star": "雷風",
    "moon": "水冰",
}


def split_tokens(text: str) -> list[str]:
    if not text:
        return []
    parts = re.split(r"[、，,;；/／]+", text)
    out: list[str] = []
    for p in parts:
        p = re.sub(r"[`*_]", "", p).strip()
        p = re.sub(r"（[^）]*）", "", p).strip()
        p = re.sub(r"\([^)]*\)", "", p).strip()
        if p and p not in out:
            out.append(p)
    return out


def compute_overlaps(items: list[dict[str, Any]], key_field: str = "prompt_keywords") -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    n = len(items)
    kw_sets = [set(item[key_field]) for item in items]
    all_pairs: list[dict[str, Any]] = []

    for i in range(n):
        overlaps_for_i: list[tuple[float, str, int, set[str]]] = []
        for j in range(n):
            if i == j:
                continue
            a, b = kw_sets[i], kw_sets[j]
            if not a or not b:
                continue
            inter = a & b
            denom = min(len(a), len(b))
            ov_pct = round(len(inter) / denom * 100.0, 1)
            jacc_pct = round(len(inter) / len(a | b) * 100.0, 1)
            overlaps_for_i.append((ov_pct, items[j]["id"], len(inter), inter))
            if i < j and ov_pct > MAX_OVERLAP_PCT:
                all_pairs.append({
                    "id_a": items[i]["id"],
                    "name_a": items[i]["name_zh"],
                    "id_b": items[j]["id"],
                    "name_b": items[j]["name_zh"],
                    "overlap_pct": ov_pct,
                    "jaccard_pct": jacc_pct,
                    "shared_count": len(inter),
                    "shared_keywords": sorted(inter),
                })

        overlaps_for_i.sort(key=lambda x: (-x[0], x[1]))
        max_ov = overlaps_for_i[0][0] if overlaps_for_i else 0.0
        over_60_cnt = sum(1 for x in overlaps_for_i if x[0] > MAX_OVERLAP_PCT)
        items[i]["kw_count"] = len(items[i][key_field])
        items[i]["max_overlap_pct"] = max_ov
        items[i]["audit_flag"] = f"⚠️ 超過{int(MAX_OVERLAP_PCT)}%警戒" if max_ov > MAX_OVERLAP_PCT else f"✅ 通過(≤{int(MAX_OVERLAP_PCT)}%)"
        items[i]["over_60_partner_count"] = over_60_cnt
        items[i]["top3_overlaps"] = [f"{pid}({pct}%)" for pct, pid, _, _ in overlaps_for_i[:3]]
        if over_60_cnt > 0 and overlaps_for_i:
            top_shared = sorted(overlaps_for_i[0][3])[:4]
            items[i]["differentiation_tip"] = f"與 {overlaps_for_i[0][1]} 重疊偏高，建議區隔：{'、'.join(top_shared)}"
        else:
            items[i]["differentiation_tip"] = "已具備足夠特徵區隔"

    all_pairs.sort(key=lambda x: (-x["overlap_pct"], x["id_a"], x["id_b"]))
    return items, all_pairs


def unescape_gdoc_md(text: str) -> str:
    """Strip backslash escapes inserted when exporting Google Docs as Markdown."""
    return re.sub(r"\\([\\`*_#\[\]()+.!-])", r"\1", text)


def extract_creature_archetypes(proto_tags: str, core_proto: str) -> tuple[str, list[str]]:
    """Split archetype tokens into a required primary archetype and secondary archetypes."""
    tokens = split_tokens(proto_tags or core_proto)
    if not tokens:
        return "", []
    primary = tokens[0]
    secondary = tokens[1:]
    if not secondary and proto_tags and core_proto:
        core_tokens = split_tokens(core_proto)
        if len(core_tokens) > 1:
            secondary = [t for t in core_tokens[1:] if t != primary]
    return primary, secondary


def audit_creature_primary_archetypes(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Enforce zero duplication on primary_archetype across all creatures."""
    by_primary: dict[str, list[dict[str, Any]]] = {}
    for it in items:
        key = it.get("primary_archetype", "").strip()
        if key:
            by_primary.setdefault(key, []).append(it)

    duplicates: list[dict[str, Any]] = []
    for key, group in sorted(by_primary.items()):
        if len(group) > 1:
            duplicates.append({
                "primary_archetype": key,
                "count": len(group),
                "ids": [g["id"] for g in group],
                "names": [g["name_zh"] for g in group],
            })
            partners = ", ".join(g["id"] for g in group)
            for g in group:
                g["primary_archetype_unique"] = False
                g["primary_archetype_audit"] = f"❌ 主原型重複({partners})"
        else:
            group[0]["primary_archetype_unique"] = True
            group[0]["primary_archetype_audit"] = "✅ 唯一"

    for it in items:
        if not it.get("primary_archetype"):
            it["primary_archetype_unique"] = False
            it["primary_archetype_audit"] = "❌ 缺主設計原型"

    # Compute secondary archetype overlap against other creatures' secondary_archetypes
    sec_sets = [set(it.get("secondary_archetypes", [])) for it in items]
    for i, it in enumerate(items):
        a = sec_sets[i]
        if not a:
            it["secondary_max_overlap_pct"] = 0.0
            continue
        max_sec = 0.0
        for j, b in enumerate(sec_sets):
            if i == j or not b:
                continue
            ov = round(len(a & b) / min(len(a), len(b)) * 100.0, 1)
            if ov > max_sec:
                max_sec = ov
        it["secondary_max_overlap_pct"] = max_sec

    flagged_cnt = sum(1 for it in items if not it.get("primary_archetype_unique", False))
    return duplicates, flagged_cnt


def infer_creature_element(cid: str) -> str:
    for el in ELEMENT_ZH:
        if f"_{el}_" in cid or cid.startswith(f"{el}_"):
            return el
    mapping = {
        "aqua_slime": "water",
        "fire_wisp": "fire",
        "frostblade_penguin": "ice",
        "earth_golem": "earth",
        "chrono_beetle": "metal",
        "shadow_eye": "shadow",
        "metal_vault": "metal",
        "ink_stele": "shadow",
        "ice_snowman": "ice",
        "light_khepri": "light",
        "verdant_aquila": "wood",
        "wind_bird": "wind",
        "solmane_lion": "fire",
        "thunder_drone": "thunder",
        "wood_puppet": "wood",
    }
    for k, v in mapping.items():
        if k in cid:
            return v
    return "unknown"


def parse_creature_prompt(path: Path, status: str, category: str, cid_override: str | None = None, rel_override: str | None = None) -> dict[str, Any]:
    txt = unescape_gdoc_md(path.read_text(encoding="utf-8"))
    lines = txt.splitlines()
    title = lines[0].lstrip("# ").strip() if lines else path.stem
    m_id = re.match(r"\[([^\]]+)\]\s*(.+)", title)
    cid = cid_override or (path.parent.name if status.startswith("已開工") else path.stem.replace(".prompt", ""))
    subject_id = m_id.group(1) if m_id else cid
    name_zh = m_id.group(2).strip() if m_id else title

    element = infer_creature_element(cid)

    def get_bullet(key: str) -> str:
        m = re.search(rf"^- \*\*{re.escape(key)}\*\*：(.+)$", txt, re.M)
        return m.group(1).strip() if m else ""

    core_proto = get_bullet("核心原型")
    proto_tags = get_bullet("設計原型標籤")
    morph_route = get_bullet("形態路由")
    palette = get_bullet("共通配色")
    vfx_palette = get_bullet("元素光效色系")
    motifs = get_bullet("標誌性紋樣")
    anchors = get_bullet("共通構造錨點")

    primary_archetype, secondary_archetypes = extract_creature_archetypes(proto_tags, core_proto)

    # Stage sizes
    stage_sizes: dict[str, str] = {}
    for st in ("juvenile", "adolescent", "adult", "overload"):
        m_st = re.search(rf"### .*?\({st}.*?\).*?\n+(?:- \*\*體型尺度\*\*：([^\n]+))", txt)
        if m_st:
            stage_sizes[st] = m_st.group(1).strip()

    # Build keywords by dimension
    dim_element_batch = [
        f"元素_{ELEMENT_ZH.get(element, element)}屬性",
        f"定位_{category}",
    ]

    dim_morph: list[str] = []
    if morph_route:
        m_base = re.search(r"base_entity=([^\s·]+)", morph_route)
        m_prim = re.search(r"primary=([^\s·]+)", morph_route)
        m_sec = re.search(r"secondary=([^\s·]+)", morph_route)
        if m_base:
            dim_morph.append(f"基底_{m_base.group(1)}")
        if m_prim:
            dim_morph.append(f"主形態_{m_prim.group(1)}")
        if m_sec and m_sec.group(1) != "none":
            dim_morph.append(f"副形態_{m_sec.group(1)}")

    for tok in split_tokens(proto_tags or core_proto)[:5]:
        dim_morph.append(f"原型_{tok}")

    dim_palette: list[str] = []
    for tok in split_tokens(palette)[:4]:
        dim_palette.append(f"配色_{tok}")
    for tok in split_tokens(vfx_palette)[:3]:
        dim_palette.append(f"光效_{tok}")

    dim_motifs: list[str] = []
    for tok in split_tokens(motifs)[:4]:
        dim_motifs.append(f"紋樣_{tok}")
    for tok in split_tokens(anchors)[:3]:
        dim_motifs.append(f"錨點_{tok}")

    dim_scale: list[str] = []
    for st, label in (("juvenile", "幼年"), ("adolescent", "少年"), ("adult", "成年"), ("overload", "超載")):
        if st in stage_sizes:
            m_cls = re.search(r"(?:`|[（(])(XS|S|M|L|XL)(?:`|[）)])", stage_sizes[st])
            if m_cls:
                dim_scale.append(f"{label}體級_{m_cls.group(1)}")

    keywords_by_dim = {
        "element_and_batch": dim_element_batch,
        "morphology_and_archetype": dim_morph,
        "palette_and_vfx": dim_palette,
        "signature_motifs_and_anchors": dim_motifs,
        "stage_scale": dim_scale,
    }
    prompt_keywords: list[str] = []
    for lst in keywords_by_dim.values():
        for kw in lst:
            if kw not in prompt_keywords:
                prompt_keywords.append(kw)

    rel_path = rel_override or str(path.relative_to(DRIVE / "creatures")).replace("\\", "/")
    return {
        "id": cid,
        "subject_id": subject_id,
        "name_zh": name_zh,
        "element": element,
        "category": category,
        "status": status,
        "source_prompt": rel_path,
        "core_archetype": core_proto,
        "primary_archetype": primary_archetype,
        "secondary_archetypes": secondary_archetypes,
        "palette": palette,
        "keywords_by_dimension": keywords_by_dim,
        "prompt_keywords": prompt_keywords,
    }


def _creature_category(name: str) -> str:
    if name.startswith("ch_starter_"):
        return "御三家(starter)"
    if "mythic" in name:
        return "神獸(mythic)"
    if "trial_boss" in name:
        return "試煉BOSS(trial_boss)"
    if name.startswith("ch_1st_batch_"):
        return "第一批(1st_batch)"
    return "一般演化線(line)"


def _load_creature_cache(json_path: Path) -> dict[str, dict[str, Any]]:
    cache: dict[str, dict[str, Any]] = {}
    if not json_path.exists():
        return cache
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        return cache
    for item in data.get("creatures", []):
        cid = item.get("id", "")
        if not cid:
            continue
        cache[cid] = item
        if cid.startswith("line_"):
            cache.setdefault(f"ch_{cid}", item)
        elif cid.startswith("ch_line_"):
            cache.setdefault(cid.removeprefix("ch_"), item)
    return cache


def _hydrate_cached_creature(cached: dict[str, Any], folder: Path) -> dict[str, Any]:
    item = dict(cached)
    cid = folder.name
    item["id"] = cid
    item["status"] = "已開工（Drive 主目錄）"
    item["category"] = item.get("category") or _creature_category(cid)
    gdocs = list(folder.glob("*.prompt.md.gdoc"))
    if gdocs:
        item["source_prompt"] = f"{cid}/{gdocs[0].name}"
    morph = [
        k.removeprefix("原型_")
        for k in item.get("keywords_by_dimension", {}).get("morphology_and_archetype", [])
        if k.startswith("原型_")
    ]
    if morph:
        item["primary_archetype"] = morph[0]
        item["secondary_archetypes"] = morph[1:]
    else:
        primary, secondary = extract_creature_archetypes("", item.get("core_archetype", ""))
        item["primary_archetype"] = primary
        item["secondary_archetypes"] = secondary
    return item


def build_creatures_table(extra_prompts_dir: Path | None = None) -> dict[str, Any]:
    c_root = DRIVE / "creatures"
    dp_root = c_root / "_designed_prompts"
    cache = _load_creature_cache(dp_root / "_creature_feature_lookup_table.json")

    items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    # 1. Active folders ch_* and line_* in Drive/creatures
    for folder in sorted(c_root.iterdir()):
        if not folder.is_dir() or folder.name in ("_prompts", "_designed_prompts", "SKILL"):
            continue
        if not (folder.name.startswith("ch_") or folder.name.startswith("line_")):
            continue
        cat = _creature_category(folder.name)
        prompts = list(folder.glob("*.prompt.md"))
        extra_prompt = (extra_prompts_dir / f"{folder.name}.prompt.md") if extra_prompts_dir else None
        if prompts:
            item = parse_creature_prompt(prompts[0], "已開工（Drive 主目錄）", cat)
        elif extra_prompt and extra_prompt.exists():
            item = parse_creature_prompt(
                extra_prompt,
                "已開工（Drive 主目錄）",
                cat,
                cid_override=folder.name,
                rel_override=f"{folder.name}/{folder.name}.prompt.md.gdoc",
            )
        elif folder.name in cache:
            item = _hydrate_cached_creature(cache[folder.name], folder)
        else:
            continue
        items.append(item)
        seen_ids.add(item["id"])

    # 2. _designed_prompts
    for sub, cat in (
        ("_starters", "御三家(starter)"),
        ("_trial_bosses", "試煉BOSS(trial_boss)"),
        ("_mythics", "神獸(mythic)"),
        ("_lines", "一般演化線(line)"),
    ):
        sub_dir = dp_root / sub
        if not sub_dir.exists():
            continue
        for p in sorted(sub_dir.glob("*.prompt.md")):
            cid = p.stem.replace(".prompt", "")
            if cid in seen_ids or f"ch_{cid}" in seen_ids:
                continue
            item = parse_creature_prompt(p, "待製作（_designed_prompts）", cat)
            items.append(item)
            seen_ids.add(item["id"])

    dup_primaries, primary_flagged = audit_creature_primary_archetypes(items)
    items, high_pairs = compute_overlaps(items)

    by_element: dict[str, Any] = {}
    for it in items:
        el = it["element"]
        b = by_element.setdefault(
            el,
            {"name_zh": ELEMENT_ZH.get(el, el), "total": 0, "primary_duplicates": 0, "flagged_over_60": 0, "passed": 0},
        )
        b["total"] += 1
        if not it.get("primary_archetype_unique", True):
            b["primary_duplicates"] += 1
        if it["max_overlap_pct"] > MAX_OVERLAP_PCT:
            b["flagged_over_60"] += 1
        if it.get("primary_archetype_unique", True) and it["max_overlap_pct"] <= MAX_OVERLAP_PCT:
            b["passed"] += 1

    kw_counts = [it["kw_count"] for it in items]
    active_cnt = sum(1 for i in items if i["status"].startswith("已開工"))
    pending_cnt = sum(1 for i in items if i["status"].startswith("待製作"))
    return {
        "schema_version": "1.0",
        "project": "cosmos_chimera_forge",
        "scope": f"creatures 全庫（已開工 {active_cnt} 條 + 待製作 {pending_cnt} 條 = 共 {len(items)} 條演化線）",
        "overlap_rule": {
            "primary_archetype_rule": "主設計原型（primary_archetype）強制不得重複（0% 重複容忍，全庫唯一）",
            "metric": "Overlap Coefficient = |A ∩ B| / min(|A|, |B|) on prompt_keywords（含副設計原型與視覺特徵）",
            "max_allowed_pct": MAX_OVERLAP_PCT,
            "min_keywords_per_item": 10,
        },
        "summary": {
            "total_creatures": len(items),
            "min_kw_count": min(kw_counts) if kw_counts else 0,
            "max_kw_count": max(kw_counts) if kw_counts else 0,
            "avg_kw_count": round(sum(kw_counts) / len(kw_counts), 1) if kw_counts else 0.0,
            "primary_archetype_flagged_count": primary_flagged,
            "duplicate_primary_archetypes": dup_primaries,
            "flagged_over_60_count": sum(1 for it in items if it["max_overlap_pct"] > MAX_OVERLAP_PCT),
            "passed_count": sum(1 for it in items if it.get("primary_archetype_unique", True) and it["max_overlap_pct"] <= MAX_OVERLAP_PCT),
            "total_high_overlap_pairs_over_60": len(high_pairs),
            "by_element": dict(sorted(by_element.items())),
        },
        "creatures": items,
        "top_high_overlap_pairs": high_pairs[:30],
    }


PROTAGONIST_NAMES: dict[str, tuple[str, str]] = {
    "chr_protagonist_amemori_sumiha": ("雨森澄羽", "Amemori Sumiha"),
    "chr_protagonist_roen": ("洛恩", "Roen"),
    "chr_protagonist_yeh_chengxi": ("葉澄汐", "Yeh Chengxi"),
}


def split_char_name_and_title(raw_label: str, category: str, explicit_title: str = "") -> tuple[str, str, str, str]:
    """Split raw display label into (name_zh, name_en, title_zh, title_en)."""
    raw = raw_label.strip()
    m_en = re.match(r"^([^(\（]+?)\s*[(\（]([^)\）]+)[)\）]\s*$", raw)
    zh_part = m_en.group(1).strip() if m_en else raw
    en_part = m_en.group(2).strip() if m_en else ""

    title_zh = explicit_title.strip()
    title_en = ""
    if category.startswith("生活任務NPC") and "·" in zh_part:
        name_zh, t_zh = [p.strip() for p in zh_part.split("·", 1)]
        if not title_zh:
            title_zh = t_zh
        en_toks = en_part.split() if en_part else []
        name_en = en_toks[0] if en_toks else ""
        title_en = " ".join(en_toks[1:]) if len(en_toks) > 1 else ""
    else:
        name_zh = zh_part
        name_en = en_part

    return name_zh, name_en, title_zh, title_en


def extract_char_narrative_keywords(cid: str, txt: str, links_by_id: dict[str, Any]) -> tuple[str, str, dict[str, list[str]]]:
    lines = txt.splitlines()
    title = lines[0].lstrip("# ").strip() if lines else cid
    # Name extraction
    m_name = re.search(r"-\s*姓名[：:]\s*([^\n]+)", txt) or re.search(r"-\s*Character name[：:]\s*([^\n]+)", txt, re.I) or re.search(r"-\s*Name[：:]\s*([^\n]+)", txt, re.I)
    m_title = re.search(r"-\s*稱號[：:]\s*([^\n]+)", txt)
    explicit_title = m_title.group(1).strip() if m_title else ""

    if m_name:
        raw_name = m_name.group(1).strip()
    elif cid in PROTAGONIST_NAMES:
        zh, en = PROTAGONIST_NAMES[cid]
        raw_name = f"{zh} ({en})"
    else:
        header = title.split("｜")[0].strip()
        if "—" in header:
            left, right = [p.strip() for p in header.split("—", 1)]
            raw_name = right if (left == cid or "Prompt" in right or "提示詞" in right) and "Prompt" not in right and "提示詞" not in right else (right if left == cid else left)
        else:
            raw_name = header

    cat = "主角(protagonist)" if cid.startswith("chr_protagonist_") else "試煉關主(warden)"
    dim_demo = [f"定位_{cat}"]

    # Gender
    if re.search(r"女性|少女|女子|女，", txt):
        dim_demo.append("性別_女")
    elif re.search(r"男性|少年|男子|男，", txt):
        dim_demo.append("性別_男")

    # Age band
    m_age = re.search(r"(\d{2})\s*歲", txt)
    if m_age:
        age = int(m_age.group(1))
        if age <= 19:
            dim_demo.append("年齡層_青少年(13-19)")
        elif age <= 35:
            dim_demo.append("年齡層_青年(20-35)")
        elif age <= 55:
            dim_demo.append("年齡層_中年(36-55)")
        else:
            dim_demo.append("年齡層_長者(56+)")
    elif "少女" in txt or "少年" in txt:
        dim_demo.append("年齡層_青少年(13-19)")

    # Ethnicity / region (check specific multi-char regions before shorter substrings)
    for eth in ("東南亞", "南亞", "東亞", "西亞", "中東", "東非", "非裔", "北歐", "歐洲", "南島", "白人", "拉丁", "原住民"):
        if eth in txt:
            dim_demo.append(f"族裔_{eth}")
            break

    # Height
    m_h = re.search(r"身高\s*(\d{3})\s*cm", txt)
    if m_h:
        h = int(m_h.group(1))
        band = "矮(<160)" if h < 160 else "中(160-174)" if h < 175 else "高(>=175)"
        dim_demo.append(f"身高尺度_{band}")

    # Element if warden
    if cid in links_by_id:
        el = links_by_id[cid].get("element", "")
        if el:
            dim_demo.append(f"關聯元素_{ELEMENT_ZH.get(el, el)}屬性")

    # Hair & eyes
    dim_hair_face: list[str] = []
    for kw, label in (
        ("高馬尾", "髮型_高馬尾"), ("側馬尾", "髮型_側馬尾"), ("雙馬尾", "髮型_雙馬尾"),
        ("低髻", "髮型_低髻"), ("丸子頭", "髮型_丸子頭"), ("辮子", "髮型_辮子"),
        ("短髮", "髮型_短髮"), ("中長髮", "髮型_中長髮"), ("長髮", "髮型_長髮"),
        ("捲髮", "髮型_捲髮"), ("挑染", "髮型_挑染"),
    ):
        if kw in txt:
            dim_hair_face.append(label)
    for kw, label in (
        ("單片", "臉部_單片眼鏡"), ("護目鏡", "臉部_護目鏡"), ("頭燈", "臉部_頭燈"),
        ("短鬚", "臉部_鬍鬚"), ("長鬚", "臉部_鬍鬚"), ("雀斑", "臉部_雀斑"), ("面紋", "臉部_面紋"),
    ):
        if kw in txt and label not in dim_hair_face:
            dim_hair_face.append(label)

    # Colors (60/30/10 or general colors)
    dim_palette: list[str] = []
    for color in (
        "玄鐵黑", "深炭灰", "炭黑", "墨黑", "深棕", "花崗褐", "羊皮米白", "米白", "象牙白",
        "鈷藍", "深海藍", "深藏青", "海軍藍", "海藍", "冰藍", "灰藍", "青綠", "翡翠綠", "青苔深灰",
        "赭紅", "陶土紅", "鮮橘紅", "橘紅", "珊瑚橘", "琥珀金", "黃銅金", "古銅金", "暖金", "金黃", "銀白", "暗紫", "紫羅蘭",
    ):
        if color in txt and f"配色_{color}" not in dim_palette:
            dim_palette.append(f"配色_{color}")
            if len(dim_palette) >= 6:
                break

    # Garment & Gear
    dim_gear: list[str] = []
    for kw, label in (
        ("風衣", "服裝_風衣"), ("水手", "服裝_水手服"), ("振袖", "服裝_振袖"), ("長衫", "服裝_長衫"),
        ("夾克", "服裝_夾克"), ("外套", "服裝_外套"), ("長袍", "服裝_長袍"), ("襯衫", "服裝_襯衫"),
        ("背心", "服裝_背心"), ("短褲", "服裝_短褲"), ("工裝長褲", "服裝_工裝長褲"), ("長裙", "服裝_長裙"), ("短裙", "服裝_短裙"),
        ("短披肩", "服裝_短披肩"), ("護肩", "服裝_護肩"), ("護腕", "服裝_護腕"), ("露指手套", "服裝_露指手套"),
        ("登山靴", "鞋履_登山靴"), ("高筒靴", "鞋履_高筒靴"), ("短靴", "鞋履_短靴"), ("工作靴", "鞋履_工作靴"),
    ):
        if kw in txt and label not in dim_gear:
            dim_gear.append(label)
    if "長褲" in txt and "服裝_工裝長褲" not in dim_gear and "服裝_長褲" not in dim_gear:
        dim_gear.append("服裝_長褲")

    for kw, label in (
        ("魔術方塊", "收服道具_魔術方塊"), ("琉璃珠", "收服道具_琉璃珠"), ("符籙", "收服道具_符籙卡片"),
        ("背包", "裝備_背包"), ("工具包", "裝備_工具包"), ("羅盤", "裝備_羅盤"), ("懷錶", "裝備_懷錶"),
    ):
        if kw in txt and label not in dim_gear:
            dim_gear.append(label)

    keywords_by_dim = {
        "demographics": dim_demo,
        "hair_and_face": dim_hair_face,
        "palette": dim_palette,
        "silhouette_and_gear": dim_gear,
    }
    return raw_name, explicit_title, keywords_by_dim


def audit_character_names_and_titles(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    """Enforce uniqueness across character names (zh/en) and titles (zh/en)."""
    name_zh_map: dict[str, list[dict[str, Any]]] = {}
    name_en_map: dict[str, list[dict[str, Any]]] = {}
    title_zh_map: dict[str, list[dict[str, Any]]] = {}
    title_en_map: dict[str, list[dict[str, Any]]] = {}

    for it in items:
        if it.get("name_zh"):
            name_zh_map.setdefault(it["name_zh"].strip(), []).append(it)
        if it.get("name_en"):
            name_en_map.setdefault(it["name_en"].strip().lower(), []).append(it)
        if it.get("title_zh"):
            title_zh_map.setdefault(it["title_zh"].strip(), []).append(it)
        if it.get("title_en"):
            title_en_map.setdefault(it["title_en"].strip().lower(), []).append(it)

    dup_names: list[dict[str, Any]] = []
    dup_titles: list[dict[str, Any]] = []
    reasons_by_id: dict[str, list[str]] = {it["id"]: [] for it in items}

    for lang, mp in (("zh", name_zh_map), ("en", name_en_map)):
        for key, group in sorted(mp.items()):
            if len(group) > 1:
                val = group[0]["name_zh"] if lang == "zh" else group[0]["name_en"]
                dup_names.append({"lang": lang, "value": val, "count": len(group), "ids": [g["id"] for g in group]})
                for g in group:
                    reasons_by_id[g["id"]].append(f"名稱({lang}):{val}")

    for lang, mp in (("zh", title_zh_map), ("en", title_en_map)):
        for key, group in sorted(mp.items()):
            if len(group) > 1:
                val = group[0]["title_zh"] if lang == "zh" else group[0]["title_en"]
                dup_titles.append({"lang": lang, "value": val, "count": len(group), "ids": [g["id"] for g in group]})
                for g in group:
                    reasons_by_id[g["id"]].append(f"稱號({lang}):{val}")

    flagged = 0
    for it in items:
        reasons = reasons_by_id.get(it["id"], [])
        if reasons:
            it["name_title_unique"] = False
            it["name_title_audit"] = "❌ 重複(" + "、".join(reasons) + ")"
            flagged += 1
        else:
            it["name_title_unique"] = True
            it["name_title_audit"] = "✅ 名稱與稱號唯一"

    return dup_names, dup_titles, flagged


def parse_character_prompt(path: Path, status: str, links_by_id: dict[str, Any]) -> dict[str, Any]:
    txt = path.read_text(encoding="utf-8")
    cid = path.parent.name if status.startswith("已開工") else path.stem.replace(".prompt", "")

    if cid.startswith("chr_quest_"):
        lines = txt.splitlines()
        title = lines[0].lstrip("# ").strip() if lines else cid
        m_id = re.match(r"\[([^\]]+)\]\s*(.+)", title)
        raw_name = m_id.group(2).strip() if m_id else title

        def get_b(k: str) -> str:
            m = re.search(rf"^- \*\*{re.escape(k)}\*\*：(.+)$", txt, re.M)
            return m.group(1).strip() if m else ""

        explicit_title = get_b("稱號")
        body = get_b("基本體貌")
        style = get_b("服裝風格")
        culture = get_b("地區文化 / 年代文化 / 外觀風格")
        sil = get_b("剪影與特徵") or get_b("剪影與隨身裝備")
        pal = get_b("服裝配色") or get_b("服裝配色 (60-30-10)")
        hair_eye = get_b("髮色與瞳色") or get_b("髮型與瞳色")
        gear = get_b("隨身裝備") or get_b("剪影與隨身裝備")

        dim_demo = ["定位_生活任務NPC(quest)"]
        if re.search(r"男[，,]", body):
            dim_demo.append("性別_男")
        elif re.search(r"女[，,]", body):
            dim_demo.append("性別_女")
        m_age = re.search(r"(\d{2})\s*歲", body)
        if m_age:
            age = int(m_age.group(1))
            band = "兒童(<13)" if age < 13 else "青少年(13-19)" if age <= 19 else "青年(20-35)" if age <= 35 else "中年(36-55)" if age <= 55 else "長者(56+)"
            dim_demo.append(f"年齡層_{band}")
        for eth in ("東南亞", "南亞", "東亞", "西亞", "中東", "東非", "非裔", "北歐", "南歐", "白人", "拉丁", "原住民", "南島", "地中海"):
            if eth in body:
                dim_demo.append(f"族裔_{eth}")
                break
        m_h = re.search(r"(\d{3})\s*cm", body)
        if m_h:
            h = int(m_h.group(1))
            dim_demo.append(f"身高尺度_{'矮(<160)' if h < 160 else '中(160-174)' if h < 175 else '高(>=175)'}")
        if culture:
            c_parts = [p.strip() for p in culture.split("/") if p.strip()]
            if len(c_parts) >= 1:
                dim_demo.append(f"地區_{c_parts[0]}")
            if len(c_parts) >= 2:
                dim_demo.append(f"年代_{c_parts[1]}")
            if len(c_parts) >= 3:
                style = c_parts[2]

        dim_hair_face = []
        for tok in split_tokens(hair_eye)[:3]:
            dim_hair_face.append(f"髮瞳_{tok}")
        dim_palette = [f"配色_{tok}" for tok in split_tokens(pal)[:4]]
        dim_gear = [f"風格_{style}"] if style else []
        for tok in split_tokens(sil)[:4]:
            dim_gear.append(f"特徵_{tok}")
        for tok in split_tokens(gear)[:3]:
            dim_gear.append(f"裝備_{tok}")

        keywords_by_dim = {
            "demographics": dim_demo,
            "hair_and_face": dim_hair_face,
            "palette": dim_palette,
            "silhouette_and_gear": dim_gear,
        }
        category = "生活任務NPC(quest)"
    else:
        raw_name, explicit_title, keywords_by_dim = extract_char_narrative_keywords(cid, txt, links_by_id)
        category = "主角(protagonist)" if cid.startswith("chr_protagonist_") else "試煉關主(warden)"

    name_zh, name_en, title_zh, title_en = split_char_name_and_title(raw_name, category, explicit_title)

    prompt_keywords: list[str] = []
    for lst in keywords_by_dim.values():
        for kw in lst:
            if kw not in prompt_keywords:
                prompt_keywords.append(kw)

    rel_path = str(path.relative_to(DRIVE / "characters")).replace("\\", "/")
    return {
        "id": cid,
        "name_zh": name_zh,
        "name_en": name_en,
        "title_zh": title_zh,
        "title_en": title_en,
        "display_name": raw_name,
        "category": category,
        "status": status,
        "source_prompt": rel_path,
        "keywords_by_dimension": keywords_by_dim,
        "prompt_keywords": prompt_keywords,
    }


def build_characters_table() -> dict[str, Any]:
    links_path = GAME_REPO / "Data" / "_catalog" / "character-creature-links.json"
    links_by_id: dict[str, Any] = {}
    if links_path.exists():
        links_data = json.loads(links_path.read_text(encoding="utf-8"))
        for w in links_data.get("trial_wardens", []):
            links_by_id[w["character_id"]] = w

    items: list[dict[str, Any]] = []
    for folder in sorted((DRIVE / "characters").glob("chr_*")):
        if not folder.is_dir():
            continue
        prompts = list(folder.glob("*.prompt.md"))
        if prompts:
            items.append(parse_character_prompt(prompts[0], "已開工（Drive 主目錄）", links_by_id))

    for p in sorted((DRIVE / "characters" / "_designed_prompts").glob("*.prompt.md")):
        items.append(parse_character_prompt(p, "待製作（_designed_prompts）", links_by_id))

    dup_names, dup_titles, name_title_flagged = audit_character_names_and_titles(items)
    items, high_pairs = compute_overlaps(items)

    by_category: dict[str, Any] = {}
    for it in items:
        cat = it["category"]
        b = by_category.setdefault(cat, {"total": 0, "name_title_flagged": 0, "flagged_over_60": 0, "passed": 0})
        b["total"] += 1
        if not it.get("name_title_unique", True):
            b["name_title_flagged"] += 1
        if it["max_overlap_pct"] > MAX_OVERLAP_PCT:
            b["flagged_over_60"] += 1
        if it.get("name_title_unique", True) and it["max_overlap_pct"] <= MAX_OVERLAP_PCT:
            b["passed"] += 1

    kw_counts = [it["kw_count"] for it in items]
    return {
        "schema_version": "1.0",
        "project": "cosmos_chimera_forge",
        "scope": f"characters 全庫（已開工 {sum(1 for i in items if i['status'].startswith('已開工'))} 位 + 待製作 {sum(1 for i in items if i['status'].startswith('待製作'))} 位 = 共 {len(items)} 位角色）",
        "overlap_rule": {
            "name_and_title_rule": "角色名稱（中／英文名）與稱號（中／英文稱號）皆強制不得重複（全庫唯一）",
            "metric": "Overlap Coefficient = |A ∩ B| / min(|A|, |B|) on prompt_keywords",
            "max_allowed_pct": MAX_OVERLAP_PCT,
            "min_keywords_per_item": 8,
        },
        "summary": {
            "total_characters": len(items),
            "min_kw_count": min(kw_counts) if kw_counts else 0,
            "max_kw_count": max(kw_counts) if kw_counts else 0,
            "avg_kw_count": round(sum(kw_counts) / len(kw_counts), 1) if kw_counts else 0.0,
            "name_title_flagged_count": name_title_flagged,
            "duplicate_names": dup_names,
            "duplicate_titles": dup_titles,
            "flagged_over_60_count": sum(1 for it in items if it["max_overlap_pct"] > MAX_OVERLAP_PCT),
            "passed_count": sum(1 for it in items if it.get("name_title_unique", True) and it["max_overlap_pct"] <= MAX_OVERLAP_PCT),
            "total_high_overlap_pairs_over_60": len(high_pairs),
            "by_category": by_category,
        },
        "characters": items,
        "top_high_overlap_pairs": high_pairs[:30],
    }


def render_creature_md(data: dict[str, Any]) -> str:
    s = data["summary"]
    lines = [
        "# 宙獸特徵檢索表（_creature_feature_lookup_table）",
        "",
        f"> **範圍**：{data['scope']}",
        f"> **主設計原型規則**：{data['overlap_rule']['primary_archetype_rule']}",
        f"> **副設計原型與視覺重疊判定**：`{data['overlap_rule']['metric']}`，上限 `{data['overlap_rule']['max_allowed_pct']}%`",
        f"> **統計**：共 {s['total_creatures']} 條演化線｜全數通過：{s['passed_count']}｜主原型重複：{s['primary_archetype_flagged_count']}｜視覺超過警戒(>60%)：{s['flagged_over_60_count']}｜高重疊配對：{s['total_high_overlap_pairs_over_60']}",
        "",
        "## 使用規範（設計新宙獸前必讀）",
        "1. 設計任何新宙獸演化線前，**必須先閱讀本表（或同目錄 `.json`）**。",
        "2. **主設計原型強制不得重複（0% 重複容忍）**：不得與任何既有宙獸共用相同的主設計原型（`primary_archetype`）。",
        "3. **副設計原型與整體視覺特徵維持 ≤ 60% 不重複限制**：檢查目標屬性與定位下已存在的副設計原型（`secondary_archetypes`）、形態路由、共通配色與標誌性紋樣，確保關鍵字重疊率不超過 60%。",
        "",
        "## 依元素統計",
        "| 元素 | 總數 | 通過 | 主原型重複 | 警戒(>60%) |",
        "|---|---:|---:|---:|---:|",
    ]
    for el, info in s["by_element"].items():
        lines.append(f"| {info['name_zh']} (`{el}`) | {info['total']} | {info['passed']} | {info['primary_duplicates']} | {info['flagged_over_60']} |")

    lines += [
        "",
        "## 宙獸清單",
        "| ID | 名稱 | 元素 | 主設計原型 | 副設計原型 | 狀態 | 主原型稽核 | 最高重疊 | 視覺稽核 |",
        "|---|---|---|---|---|---|---|---:|---|",
    ]
    for c in data["creatures"]:
        sec_str = "、".join(c.get("secondary_archetypes", [])) or "—"
        lines.append(
            f"| `{c['id']}` | {c['name_zh']} | {c['element']} | {c.get('primary_archetype', '—')} | {sec_str} | {c['status']} | {c.get('primary_archetype_audit', '—')} | {c['max_overlap_pct']}% | {c['audit_flag']} |"
        )
    return "\n".join(lines) + "\n"


def render_character_md(data: dict[str, Any]) -> str:
    s = data["summary"]
    lines = [
        "# 角色特徵檢索表（_character_feature_lookup_table）",
        "",
        f"> **範圍**：{data['scope']}",
        f"> **名稱與稱號規則**：{data['overlap_rule']['name_and_title_rule']}",
        f"> **視覺特徵重疊判定**：`{data['overlap_rule']['metric']}`，上限 `{data['overlap_rule']['max_allowed_pct']}%`",
        f"> **統計**：共 {s['total_characters']} 位角色｜全數通過：{s['passed_count']}｜名稱／稱號重複：{s['name_title_flagged_count']}｜視覺超過警戒(>60%)：{s['flagged_over_60_count']}｜高重疊配對：{s['total_high_overlap_pairs_over_60']}",
        "",
        "## 使用規範（設計新角色前必讀）",
        "1. 設計任何新角色前，**必須先閱讀本表（或同目錄 `.json`）**。",
        "2. **名稱與稱號皆強制不得重複**：中／英文名稱與中／英文稱號均須全庫唯一。",
        "3. 檢查已存在的「性別／年齡／族裔分佈」、「髮型與臉部特徵」、「服裝配色」與「隨身裝備」，避免與現有角色剪影或配色撞車超過 60%。",
        "",
        "## 依定位統計",
        "| 定位 | 總數 | 通過 | 名稱／稱號重複 | 警戒(>60%) |",
        "|---|---:|---:|---:|---:|",
    ]
    for cat, info in s["by_category"].items():
        lines.append(f"| {cat} | {info['total']} | {info['passed']} | {info['name_title_flagged']} | {info['flagged_over_60']} |")

    lines += [
        "",
        "## 角色清單",
        "| ID | 名稱 | 稱號 | 定位 | 名稱/稱號稽核 | 最高重疊 | 視覺稽核 |",
        "|---|---|---|---|---|---:|---|",
    ]
    for c in data["characters"]:
        name_disp = f"{c['name_zh']} ({c['name_en']})" if c.get("name_en") else c["name_zh"]
        if c.get("title_zh") and c.get("title_en"):
            title_disp = f"{c['title_zh']} ({c['title_en']})"
        else:
            title_disp = c.get("title_zh") or c.get("title_en") or "—"
        lines.append(
            f"| `{c['id']}` | {name_disp} | {title_disp} | {c['category']} | {c.get('name_title_audit', '—')} | {c['max_overlap_pct']}% | {c['audit_flag']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build creature and character feature lookup tables.")
    parser.add_argument("--extra-prompts-dir", type=Path, default=None, help="Directory with exported *.prompt.md files for .gdoc-backed creatures.")
    parser.add_argument("--creature-md-out", type=Path, default=None, help="Optional path to write creature lookup Markdown (avoids duplicating .md.gdoc).")
    args = parser.parse_args()

    creatures_data = build_creatures_table(extra_prompts_dir=args.extra_prompts_dir)
    c_out_dir = DRIVE / "creatures" / "_designed_prompts"
    (c_out_dir / "_creature_feature_lookup_table.json").write_text(
        json.dumps(creatures_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    creature_md_text = render_creature_md(creatures_data)
    gdoc_md = c_out_dir / "_creature_feature_lookup_table.md.gdoc"
    if args.creature_md_out:
        args.creature_md_out.parent.mkdir(parents=True, exist_ok=True)
        args.creature_md_out.write_text(creature_md_text, encoding="utf-8")
    elif not gdoc_md.exists():
        (c_out_dir / "_creature_feature_lookup_table.md").write_text(creature_md_text, encoding="utf-8")

    chars_data = build_characters_table()
    ch_out_dir = DRIVE / "characters" / "_designed_prompts"
    (ch_out_dir / "_character_feature_lookup_table.json").write_text(
        json.dumps(chars_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ch_out_dir / "_character_feature_lookup_table.md").write_text(
        render_character_md(chars_data), encoding="utf-8"
    )

    print("Creatures summary:", json.dumps(creatures_data["summary"], ensure_ascii=False))
    print("Characters summary:", json.dumps(chars_data["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
