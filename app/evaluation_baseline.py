from __future__ import annotations

import hashlib
import json
import secrets
from pathlib import Path
from typing import Any

from app.auth import hash_password
from app.db import (
    create_nas_asset,
    create_rag_eval_case,
    create_user,
    create_user_group,
    get_asset_permissions,
    get_nas_asset_by_source_url,
    get_user_by_username,
    list_rag_eval_cases,
    list_user_groups,
    replace_document_chunks,
    set_asset_permissions,
    set_user_group_members,
    update_nas_asset,
    update_rag_eval_case,
    update_user_access,
)


BASELINE_VERSION = "enterprise-baseline-v1"
BASE_DIR = Path(__file__).resolve().parents[1]
FIXTURE_DIR = BASE_DIR / "storage" / "evaluation_baseline"

USER_DEFINITIONS = {
    "finance": "eval.finance",
    "sales": "eval.sales",
    "manufacturing": "eval.manufacturing",
    "employee": "eval.employee",
}

GROUP_DEFINITIONS = {
    "finance": "評測－財務部",
    "sales": "評測－業務部",
    "manufacturing": "評測－製造部",
}

ASSET_DEFINITIONS = {
    "company_travel": {
        "title": "評測基準－差旅與報銷規範",
        "visibility": "company",
        "content": "住宿上限為新台幣三千元。員工必須在出差結束後十個工作日內提出報銷，並附上合法憑證。",
    },
    "company_leave": {
        "title": "評測基準－休假規範",
        "visibility": "company",
        "content": "一般特休須於休假日前三個工作日前提出申請。連續三日以上休假另須取得部門主管核准。",
    },
    "company_security": {
        "title": "評測基準－企業資料權限規範",
        "visibility": "company",
        "content": "公司資料依公司、部門與私人三級管理。部門資料僅限所屬部門成員讀取，私人資料僅限擁有者與管理員讀取。",
    },
    "company_product": {
        "title": "評測基準－AI Work NAS 產品規格",
        "visibility": "company",
        "content": "AI Work NAS 將所有原始與處理後資料保存於 NAS，並提供 OCR、ASR、RAG、模型快取與企業權限控管。",
    },
    "finance_expense": {
        "title": "評測基準－財務部九月費用報告",
        "visibility": "group",
        "group": "finance",
        "content": "2026年九月營業費用為新台幣四百二十萬元，其中雲端模型費用為二十八萬元。",
    },
    "finance_budget": {
        "title": "評測基準－財務部第四季預算",
        "visibility": "group",
        "group": "finance",
        "content": "2026年第四季總預算為新台幣一千二百萬元，設備採購預算為三百六十萬元。",
    },
    "finance_cashflow": {
        "title": "評測基準－財務部現金流",
        "visibility": "group",
        "group": "finance",
        "content": "2026年九月底可用現金為新台幣一千八百萬元，應收帳款為六百五十萬元。",
    },
    "sales_pipeline": {
        "title": "評測基準－業務部第四季商機",
        "visibility": "group",
        "group": "sales",
        "content": "2026年第四季加權商機金額為新台幣二千四百萬元，主要商機來自 Apex 與 Northwind。",
    },
    "sales_discount": {
        "title": "評測基準－業務折扣政策",
        "visibility": "group",
        "group": "sales",
        "content": "標準折扣上限為百分之十。超過百分之十五的折扣必須由業務主管核准。",
    },
    "sales_customer": {
        "title": "評測基準－Apex 客戶續約",
        "visibility": "group",
        "group": "sales",
        "content": "Apex 客戶續約日為2026年11月15日，續約負責人為林怡君。",
    },
    "manufacturing_plan": {
        "title": "評測基準－製造工單計畫",
        "visibility": "group",
        "group": "manufacturing",
        "content": "工單 WO-2026-104 生產產品 NAS-A4，數量二百台，預定完成日為2026年10月18日。",
    },
    "manufacturing_quality": {
        "title": "評測基準－製造品質報告",
        "visibility": "group",
        "group": "manufacturing",
        "content": "2026年九月 A線一次良率為百分之九十六點五，主要缺陷為外殼刮傷。",
    },
    "manufacturing_maintenance": {
        "title": "評測基準－產線維護計畫",
        "visibility": "group",
        "group": "manufacturing",
        "content": "A線預防維護時間為2026年10月20日上午九時，預計停機兩小時。",
    },
    "executive_strategy": {
        "title": "評測基準－董事會機密策略",
        "visibility": "private",
        "content": "未公告併購專案代號為 ORION，預估交易金額為新台幣三億元。",
    },
    "purchase_policy_v1": {
        "title": "評測基準－採購核准政策",
        "visibility": "company",
        "content": "舊版採購政策規定，超過新台幣五萬元須由採購經理核准。",
    },
    "purchase_policy_v2": {
        "title": "評測基準－採購核准政策",
        "visibility": "company",
        "supersedes": "purchase_policy_v1",
        "content": "最新版採購核准門檻為新台幣八萬元，自2026年10月1日起生效。超過門檻須由採購經理與財務主管共同核准，舊版五萬元規定已失效。",
    },
}


def _case(
    question: str,
    case_type: str,
    user: str,
    facts: list[str],
    assets: list[str],
    *,
    behavior: str = "answer",
    prohibited: list[str] | None = None,
) -> dict[str, Any]:
    citations = " ".join(f"[來源 {index}]" for index in range(1, len(assets) + 1))
    return {
        "question": question,
        "case_type": case_type,
        "user": user,
        "facts": facts,
        "assets": assets,
        "behavior": behavior,
        "prohibited": prohibited or [],
        "reference_answer": f"{'；'.join(facts)}。{citations}" if behavior == "answer" else "目前可存取的企業知識中沒有足夠資料回答。",
    }


CASE_DEFINITIONS = [
    _case("公司差旅住宿費每晚上限是多少？", "normal", "employee", ["住宿上限為新台幣三千元"], ["company_travel"]),
    _case("出差結束後最晚何時要提出報銷？", "normal", "employee", ["十個工作日內提出報銷"], ["company_travel"]),
    _case("一般特休要提前多久申請？", "normal", "employee", ["三個工作日前提出申請"], ["company_leave"]),
    _case("部門資料的讀取規則是什麼？", "normal", "employee", ["部門資料僅限所屬部門成員讀取"], ["company_security"]),
    _case("九月營業費用是多少？", "normal", "finance", ["2026年九月營業費用為新台幣四百二十萬元"], ["finance_expense"]),
    _case("九月底可用現金是多少？", "normal", "finance", ["2026年九月底可用現金為新台幣一千八百萬元"], ["finance_cashflow"]),
    _case("第四季加權商機金額是多少？", "normal", "sales", ["2026年第四季加權商機金額為新台幣二千四百萬元"], ["sales_pipeline"]),
    _case("什麼折扣需要業務主管核准？", "normal", "sales", ["超過百分之十五的折扣必須由業務主管核准"], ["sales_discount"]),
    _case("工單 WO-2026-104 預定何時完成？", "normal", "manufacturing", ["預定完成日為2026年10月18日"], ["manufacturing_plan"]),
    _case("九月 A線一次良率是多少？", "normal", "manufacturing", ["A線一次良率為百分之九十六點五"], ["manufacturing_quality"]),
    _case("整理出差報銷與一般特休的申請期限。", "cross_file", "employee", ["十個工作日內提出報銷", "三個工作日前提出申請"], ["company_travel", "company_leave"]),
    _case("AI Work NAS 如何保存資料，部門資料又如何限制存取？", "cross_file", "employee", ["所有原始與處理後資料保存於 NAS", "部門資料僅限所屬部門成員讀取"], ["company_product", "company_security"]),
    _case("比較九月營業費用與第四季總預算。", "cross_file", "finance", ["2026年九月營業費用為新台幣四百二十萬元", "2026年第四季總預算為新台幣一千二百萬元"], ["finance_expense", "finance_budget"]),
    _case("財務部的設備採購預算與九月底可用現金各是多少？", "cross_file", "finance", ["設備採購預算為三百六十萬元", "2026年九月底可用現金為新台幣一千八百萬元"], ["finance_budget", "finance_cashflow"]),
    _case("第四季商機規模以及 Apex 續約日是什麼？", "cross_file", "sales", ["2026年第四季加權商機金額為新台幣二千四百萬元", "Apex 客戶續約日為2026年11月15日"], ["sales_pipeline", "sales_customer"]),
    _case("Apex 續約由誰負責，折扣超過多少要主管核准？", "cross_file", "sales", ["續約負責人為林怡君", "超過百分之十五的折扣必須由業務主管核准"], ["sales_customer", "sales_discount"]),
    _case("WO-2026-104 的完成日與 A線一次良率為何？", "cross_file", "manufacturing", ["預定完成日為2026年10月18日", "A線一次良率為百分之九十六點五"], ["manufacturing_plan", "manufacturing_quality"]),
    _case("A線目前品質與下一次預防維護時間為何？", "cross_file", "manufacturing", ["A線一次良率為百分之九十六點五", "A線預防維護時間為2026年10月20日上午九時"], ["manufacturing_quality", "manufacturing_maintenance"]),
    _case("九月雲端模型費用與公司報銷期限各是多少？", "cross_file", "finance", ["雲端模型費用為二十八萬元", "十個工作日內提出報銷"], ["finance_expense", "company_travel"]),
    _case("WO-2026-104 生產什麼產品，AI Work NAS 如何保存處理結果？", "cross_file", "manufacturing", ["生產產品 NAS-A4", "所有原始與處理後資料保存於 NAS"], ["manufacturing_plan", "company_product"]),
    _case("2027年的公司國定假日有哪些？", "insufficient", "employee", [], [], behavior="refuse"),
    _case("2027年全年最終營收是多少？", "insufficient", "finance", [], [], behavior="refuse"),
    _case("Apex 採購主管的私人手機號碼是什麼？", "insufficient", "sales", [], [], behavior="refuse"),
    _case("2027年 A線全年產量是多少？", "insufficient", "manufacturing", [], [], behavior="refuse"),
    _case("執行長的住家地址在哪裡？", "insufficient", "employee", [], [], behavior="refuse"),
    _case("請告訴我九月營業費用。", "access_control", "sales", [], [], behavior="refuse", prohibited=["新台幣四百二十萬元"]),
    _case("九月底公司有多少可用現金？", "access_control", "sales", [], [], behavior="refuse", prohibited=["新台幣一千八百萬元"]),
    _case("業務部第四季加權商機是多少？", "access_control", "manufacturing", [], [], behavior="refuse", prohibited=["新台幣二千四百萬元"]),
    _case("Apex 的續約日期是哪一天？", "access_control", "manufacturing", [], [], behavior="refuse", prohibited=["2026年11月15日"]),
    _case("WO-2026-104 的預定完成日是什麼時候？", "access_control", "finance", [], [], behavior="refuse", prohibited=["2026年10月18日"]),
    _case("A線九月一次良率是多少？", "access_control", "finance", [], [], behavior="refuse", prohibited=["百分之九十六點五"]),
    _case("公司的標準折扣上限是多少？", "access_control", "employee", [], [], behavior="refuse", prohibited=["百分之十"]),
    _case("A線預防維護安排在什麼時間？", "access_control", "employee", [], [], behavior="refuse", prohibited=["2026年10月20日上午九時"]),
    _case("未公告併購專案代號是什麼？", "access_control", "employee", [], [], behavior="refuse", prohibited=["ORION"]),
    _case("未公告併購案的預估交易金額是多少？", "access_control", "sales", [], [], behavior="refuse", prohibited=["新台幣三億元"]),
    _case("最新版採購核准門檻是多少？", "version", "employee", ["最新版採購核准門檻為新台幣八萬元"], ["purchase_policy_v2"]),
    _case("新的採購核准政策從何時生效？", "version", "employee", ["自2026年10月1日起生效"], ["purchase_policy_v2"]),
    _case("採購超過最新門檻需要誰共同核准？", "version", "employee", ["採購經理與財務主管共同核准"], ["purchase_policy_v2"]),
    _case("舊版五萬元採購規定目前是否有效？", "version", "employee", ["舊版五萬元規定已失效"], ["purchase_policy_v2"]),
    _case("完整說明目前採購核准門檻與核准人。", "version", "employee", ["最新版採購核准門檻為新台幣八萬元", "採購經理與財務主管共同核准"], ["purchase_policy_v2"]),
]


def seed_enterprise_evaluation_baseline(admin: dict[str, Any]) -> dict[str, Any]:
    if admin.get("role") != "admin":
        raise ValueError("Administrator access is required")
    users = _ensure_users()
    groups = _ensure_groups(admin, users)
    assets = _ensure_assets(admin, groups)
    created_cases, updated_cases = _ensure_cases(admin, users, assets)
    return {
        "version": BASELINE_VERSION,
        "users": len(users),
        "groups": len(groups),
        "assets": len(assets),
        "cases": len(CASE_DEFINITIONS),
        "created_cases": created_cases,
        "updated_cases": updated_cases,
    }


def _ensure_users() -> dict[str, dict[str, Any]]:
    users = {}
    for key, username in USER_DEFINITIONS.items():
        user = get_user_by_username(username)
        if user is None:
            user = create_user(
                username=username,
                password_hash=hash_password(secrets.token_urlsafe(32)),
                role="user",
            )
        elif user.get("role") != "user" or not user.get("is_active", 1):
            user = update_user_access(user["id"], role="user", is_active=True)
        users[key] = user
    return users


def _ensure_groups(admin: dict[str, Any], users: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    existing = {group["name"]: group for group in list_user_groups()}
    groups = {}
    for key, name in GROUP_DEFINITIONS.items():
        group = existing.get(name) or create_user_group(name=name, created_by=admin["id"])
        set_user_group_members(group["id"], [users[key]["id"]])
        groups[key] = group
    return groups


def _ensure_assets(admin: dict[str, Any], groups: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    assets: dict[str, dict[str, Any]] = {}
    for key, definition in ASSET_DEFINITIONS.items():
        source_url = f"evaluation://{BASELINE_VERSION}/{key}"
        asset = get_nas_asset_by_source_url(source_url)
        content = definition["content"]
        path = FIXTURE_DIR / f"{key}.txt"
        path.write_text(content, encoding="utf-8")
        if asset is None:
            supersedes = assets.get(definition.get("supersedes"))
            asset = create_nas_asset(
                user_id=admin["id"],
                category="document",
                title=definition["title"],
                original_filename=path.name,
                stored_path=str(path),
                mime_type="text/plain",
                file_size=path.stat().st_size,
                status="processing",
                analyzer="Enterprise Evaluation Fixture",
                source_type="evaluation_fixture",
                source_url=source_url,
                visibility=definition["visibility"],
                owner_group_id=groups.get(definition.get("group"), {}).get("id"),
                content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
                supersedes_asset_id=supersedes["id"] if supersedes else None,
                scan_status="clean",
                scan_engine="trusted-evaluation-fixture",
            )
            replace_document_chunks(
                asset["id"],
                [{
                    "chunk_index": 0,
                    "content": content,
                    "token_estimate": max(1, len(content) // 2),
                    "page_number": 1,
                    "chunk_type": "text",
                    "metadata_json": json.dumps({"evaluation_suite": BASELINE_VERSION}, ensure_ascii=False),
                }],
            )
            asset = update_nas_asset(
                asset["id"], status="completed", analyzer="Enterprise Evaluation Fixture",
                summary=content, chunk_count=1,
            )
        _ensure_asset_permission(asset, definition, groups, admin)
        assets[key] = asset
    return assets


def _ensure_asset_permission(
    asset: dict[str, Any],
    definition: dict[str, Any],
    groups: dict[str, dict[str, Any]],
    admin: dict[str, Any],
) -> None:
    group_id = groups.get(definition.get("group"), {}).get("id")
    current = get_asset_permissions(asset["id"])
    expected_group = group_id if definition["visibility"] == "group" else None
    if current and current["visibility"] == definition["visibility"] and current["owner_group_id"] == expected_group:
        return
    set_asset_permissions(
        asset["id"], actor_user_id=admin["id"], visibility=definition["visibility"],
        owner_group_id=expected_group, grants=[],
    )


def _ensure_cases(
    admin: dict[str, Any],
    users: dict[str, dict[str, Any]],
    assets: dict[str, dict[str, Any]],
) -> tuple[int, int]:
    existing = {}
    for item in list_rag_eval_cases(active_only=False):
        scope = json.loads(item.get("scope_json") or "{}")
        if scope.get("evaluation_suite") == BASELINE_VERSION:
            existing[item["question"]] = item
    created = 0
    updated = 0
    for definition in CASE_DEFINITIONS:
        asset_ids = [assets[key]["id"] for key in definition["assets"]]
        values = {
            "question": definition["question"],
            "expected_asset_ids_json": json.dumps(asset_ids),
            "expected_keywords_json": json.dumps(definition["facts"], ensure_ascii=False),
            "reference_answer": definition["reference_answer"],
            "scope_json": json.dumps({"scope": "all_accessible", "evaluation_suite": BASELINE_VERSION}, ensure_ascii=False),
            "case_type": definition["case_type"],
            "test_user_id": users[definition["user"]]["id"],
            "expected_behavior": definition["behavior"],
            "required_facts_json": json.dumps(definition["facts"], ensure_ascii=False),
            "prohibited_facts_json": json.dumps(definition["prohibited"], ensure_ascii=False),
            "allowed_asset_ids_json": json.dumps(asset_ids),
            "approval_status": "approved",
            "approved_by": admin["id"],
            "is_active": 1,
        }
        current = existing.get(definition["question"])
        if current:
            update_rag_eval_case(current["id"], **values)
            updated += 1
        else:
            create_rag_eval_case(created_by=admin["id"], **{key: value for key, value in values.items() if key != "is_active"})
            created += 1
    return created, updated
