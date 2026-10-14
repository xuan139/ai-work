"""Authored teaching notes, not FHIR resources or clinical recommendations."""

PROFILES = {
    "demo-p001": {
        "interview": [
            {"speaker": "訪談員", "text": "這次回診希望先了解哪些事情？"},
            {"speaker": "病患甲", "text": "我想確認上次檢查的報告，也想把以前住院的資料一起整理。"},
            {"speaker": "訪談員", "text": "平常的飲食習慣與需要特別註記的食物有哪些？"},
            {"speaker": "病患甲", "text": "平日常外食。我記得吃花生後曾不舒服，原因沒有確認，希望先記錄並由醫療人員核對。"},
            {"speaker": "訪談員", "text": "已記為病患自述，尚未確認為過敏；不將這段訪談作為診斷。"},
        ],
        "admissions": [
            {"id": "demo-adm001", "start": "2026-03-02", "end": "2026-03-04", "department": "一般內科", "reason": "短期留院觀察（教學情境）", "status": "已出院", "note": "未提供正式出院病摘或診斷；不推測原因。"},
            {"id": "demo-adm002", "start": "2025-08-11", "end": "2025-08-12", "department": "檢查病房", "reason": "住院檢查流程示範", "status": "已出院", "note": "僅供歷史資料串接展示，與目前 X 光無因果關聯。"},
        ],
        "diet": [
            {"category": "食物反應／待核對", "text": "花生相關不適，僅為病患自述，非已確診食物過敏。", "status": "待醫療人員確認"},
            {"category": "飲食習慣", "text": "平日常外食；未提供正式營養評估。", "status": "病患自述"},
            {"category": "醫囑性飲食限制", "text": "未提供正式醫囑；不自動產生禁食、限水或治療性飲食建議。", "status": "未提供"},
        ],
    },
    "demo-p002": {
        "interview": [
            {"speaker": "訪談員", "text": "這次想查閱哪些資料？"},
            {"speaker": "病患乙", "text": "我想看之前住院與這次檢查的記錄，確認是否都已收齊。"},
            {"speaker": "訪談員", "text": "有沒有想讓工作人員知道的餐食偏好？"},
            {"speaker": "病患乙", "text": "我吃蛋奶素，沒有帶過敏檢查資料。"},
            {"speaker": "訪談員", "text": "會把蛋奶素記為餐食偏好；沒有檢查資料不代表沒有過敏。"},
        ],
        "admissions": [
            {"id": "demo-adm003", "start": "2026-06-18", "end": "2026-06-20", "department": "一般內科", "reason": "觀察與資料彙整流程示範", "status": "已出院", "note": "正式診斷、治療內容與出院醫囑均未提供。"},
        ],
        "diet": [
            {"category": "餐食偏好", "text": "蛋奶素，僅為飲食偏好，不是醫療禁忌。", "status": "病患自述"},
            {"category": "食物過敏資料", "text": "未提供；不能解讀為已排除過敏。", "status": "待核對"},
            {"category": "醫囑性飲食限制", "text": "未提供正式醫囑。", "status": "未提供"},
        ],
    },
    "demo-p003": {
        "interview": [
            {"speaker": "訪談員", "text": "這次希望先確認什麼？"},
            {"speaker": "病患丙", "text": "我想知道影像報告是否完成，還有回診時間。"},
            {"speaker": "訪談員", "text": "目前教學影像報告仍待完成。有帶住院或飲食相關記錄嗎？"},
            {"speaker": "病患丙", "text": "今天沒有帶，之後再提供。"},
            {"speaker": "訪談員", "text": "會標示資料未提供，不會當作從未住院或沒有飲食禁忌。"},
        ],
        "admissions": [],
        "diet": [
            {"category": "食物過敏與餐食偏好", "text": "資料未提供，待訪談補齊。", "status": "待核對"},
            {"category": "醫囑性飲食限制", "text": "未提供正式醫囑。", "status": "未提供"},
        ],
    },
}

for patient_id, profile in PROFILES.items():
    profile.update(patient_id=patient_id, source_id="teaching-profile/" + patient_id,
                   recorded_at="2026-10-14T09:00:00+08:00", version=1, demo=True,
                   source="作者編寫的虛構教學紀錄；非正式病歷或醫囑",
                   admission_history_note="僅列出本 Demo 已提供的住院資料；空白不代表從未住院。")
