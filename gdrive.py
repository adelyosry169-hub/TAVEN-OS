"""
gdrive.py
---------
بيربط ملف TAVEN.xlsx بجوجل درايف عشان يبقى مصدر دائم للبيانات، لأن
تخزين Streamlit Cloud مؤقت وبيتصفر لما التطبيق يعمل Reboot أو ينام
ويصحى تاني. لو الإعدادات (secrets) مش متظبطة لسه، كل الدوال هنا
بترجع False بهدوء والتطبيق يشتغل بالملف المحلي بس من غير أي كراش.
"""

import io
import streamlit as st

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

    _LIBS_AVAILABLE = True
except ImportError:
    _LIBS_AVAILABLE = False

SCOPES = ["https://www.googleapis.com/auth/drive"]


def is_configured() -> bool:
    """بيرجع True لو المكتبات متثبتة ولو الـ secrets المطلوبة موجودة."""
    if not _LIBS_AVAILABLE:
        return False
    try:
        return "gcp_service_account" in st.secrets and "drive_file_id" in st.secrets
    except Exception:
        return False


def _get_service():
    if not is_configured():
        return None
    try:
        creds = service_account.Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=SCOPES
        )
        return build("drive", "v3", credentials=creds, cache_discovery=False)
    except Exception as e:
        st.session_state["_gdrive_last_error"] = str(e)
        return None


def download_file(local_path: str) -> bool:
    """ينزل آخر نسخة من TAVEN.xlsx من جوجل درايف. بيرجع True لو نجح."""
    service = _get_service()
    if service is None:
        return False
    try:
        file_id = st.secrets["drive_file_id"]
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(local_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.close()
        return True
    except Exception as e:
        st.session_state["_gdrive_last_error"] = str(e)
        return False


def upload_file(local_path: str) -> bool:
    """يرفع النسخة المحلية المحدثة على جوجل درايف. بيرجع True لو نجح."""
    service = _get_service()
    if service is None:
        return False
    try:
        file_id = st.secrets["drive_file_id"]
        media = MediaIoBaseUpload(
            io.FileIO(local_path, "rb"),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            resumable=True,
        )
        service.files().update(fileId=file_id, media_body=media).execute()
        return True
    except Exception as e:
        st.session_state["_gdrive_last_error"] = str(e)
        return False


def status_message() -> str:
    """رسالة بسيطة نقدر نعرضها في الصفحة عن حالة الربط بجوجل درايف."""
    if not _LIBS_AVAILABLE:
        return "⚪ مكتبات جوجل درايف مش متثبتة (تأكد من requirements.txt)."
    if not is_configured():
        return "⚪ جوجل درايف مش متربط لسه — التطبيق شغال بالملف المحلي فقط."
    err = st.session_state.get("_gdrive_last_error")
    if err:
        return f"🔴 فيه مشكلة في الاتصال بجوجل درايف: {err}"
    return "🟢 متصل بجوجل درايف — البيانات بتتحفظ هناك تلقائيًا."
