# MIRA Maintenance Guide

## Scripts

| Script | Purpose | Schedule |
|--------|---------|---------|
| health_check.py | Verify collection integrity | Daily |
| reingest.py | Re-ingest changed files | Weekly |
| full_reingest.py | Rebuild entire collection | Monthly |
| cache_manager.py | Manage embedding cache | Daily |
| verify_chunks.py | Confirm all projects present | After ingest |

## Daily crontab
0 6 * * * python3 maintenance/health_check.py
0 6 * * * python3 maintenance/cache_manager.py --auto

## After updating project files
python3 maintenance/reingest.py
python3 maintenance/cache_manager.py --clear-all
python3 maintenance/verify_chunks.py

## Emergency recovery
python3 maintenance/full_reingest.py
python3 maintenance/verify_chunks.py
