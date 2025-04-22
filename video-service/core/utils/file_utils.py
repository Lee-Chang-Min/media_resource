import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException, status

async def save_upload_file(
    upload_file: UploadFile,
    folder: str = "video_files"
) -> str:
    """
    업로드된 파일을 청크 단위로 저장하고, 연/월별 하위 폴더를 만들어 파일 경로를 반환합니다.
    """
    # 1) 연/월별 폴더 경로 구성
    now = datetime.now(timezone.utc)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    base_dir = Path("file") / folder / year / month

    try:
        base_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"디렉토리 생성 실패: {e}"
        )

    # 2) 고유 파일명 생성 (타임스탬프 + UUID + 확장자)
    ext = Path(upload_file.filename).suffix
    timestamp = now.strftime("%Y%m%d%H%M%S")
    unique_filename = f"{timestamp}_{uuid.uuid4().hex}{ext}"
    file_path = base_dir / unique_filename

    # 3) 비동기 청크 쓰기 (1MB씩)
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await upload_file.read(1024 * 1024):
                await out_file.write(chunk)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 저장 중 오류 발생: {e}"
        )

    return str(file_path)
