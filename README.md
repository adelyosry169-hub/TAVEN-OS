# TAVEN CO — Professional Light ERP UI

This package is a redesigned Streamlit front-end and app structure based on the supplied TAVEN OS v2 project.

## What changed
- Direct-open dashboard: no login/signup/password screen.
- Premium light ERP/SaaS visual system.
- TAVEN CO branding and consistent navigation.
- Dashboard KPIs, cash position, revenue vs expenses, quick access.
- Cleaner Input & Output workflow with automatic Excel/Drive persistence.
- Redesigned Team Chat, Files & Analysis, Ideas, Ads Manager, Tasks, Vision and Analytics.
- Preserves the existing TAVEN.xlsx sheet model and Google Drive persistence.
- No fake external integrations are presented as live integrations.

## Run
```bash
pip install -r requirements.txt
streamlit run Home.py
```

If using Google Drive, place the service-account values in Streamlit secrets and set `drive_file_id`.
