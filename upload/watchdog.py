# pip install watchdog

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            # Trigger your upload function
            upload_file(event.src_path)

observer = Observer()
observer.schedule(NewFileHandler(), path="path/to/watch", recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
