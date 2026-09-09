import asyncio
from pathlib import Path

from app.db import get_meeting, update_meeting_status
from app.notifications import manager


async def transcribe_audio_file(audio_path: Path) -> str:
    await asyncio.sleep(1.2)
    file_size = audio_path.stat().st_size if audio_path.exists() else 0
    return (
        "這是 demo 階段的模擬轉寫結果。\n\n"
        f"系統已保存原始錄音檔案：{audio_path.name}，檔案大小 {file_size} bytes。"
        "後續接入真實語音轉文字工具時，只需要替換 app/transcription.py 中的 adapter。"
    )


async def process_meeting_transcription(meeting_id: int) -> None:
    meeting = get_meeting(meeting_id)
    if not meeting:
        return

    try:
        transcript = await transcribe_audio_file(Path(meeting["audio_path"]))
        updated = update_meeting_status(meeting_id, status="completed", transcript=transcript)
        await manager.broadcast(
            {
                "type": "meeting_completed",
                "meeting_id": meeting_id,
                "title": meeting["title"],
                "message": f"會議《{meeting['title']}》轉寫完成",
                "meeting": updated,
            }
        )
    except Exception as exc:
        updated = update_meeting_status(meeting_id, status="failed", error_message=str(exc))
        await manager.broadcast(
            {
                "type": "meeting_failed",
                "meeting_id": meeting_id,
                "title": meeting["title"],
                "message": f"會議《{meeting['title']}》處理失敗",
                "meeting": updated,
            }
        )
