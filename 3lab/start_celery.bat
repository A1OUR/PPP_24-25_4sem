@echo off
echo Starting Celery worker...
python -m celery -A tasks worker --loglevel=info --pool=solo
pause