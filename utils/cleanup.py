import os
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

def cleanup_old_files(upload_folder, hours=48):
    now = datetime.now()
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if now - file_mtime > timedelta(hours=hours):
                os.remove(file_path)
                print(f"Arquivo {filename} removido por ter mais de {hours} horas.")

def start_cleanup_scheduler(upload_folder):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=cleanup_old_files,
        args=[upload_folder],
        trigger='interval',
        hours=24,
        id='cleanup_old_files',
        name='Clean up old files',
        replace_existing=True
    )
    scheduler.start()
    return scheduler