import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
from auto_indexer import process_pdf
from s3_uploader import upload_file
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import time


class PDFHandler(FileSystemEventHandler):

    def on_created(self, event):

        if not event.is_directory:

            print(
                f"\nNew File Detected:\n{event.src_path}\n"
            )

            upload_file(
                event.src_path
            )

            print(
                "\nUploaded to S3 Successfully\n"
            )

            process_pdf(
                event.src_path
            )

            print(
                "\nKnowledge Base Updated\n"
)

folder_to_watch = "uploads"

event_handler = PDFHandler()

observer = Observer()

observer.schedule(
    event_handler,
    folder_to_watch,
    recursive=False
)

observer.start()

print(
    f"Watching folder: {folder_to_watch}"
)

try:

    while True:

        time.sleep(1)

except KeyboardInterrupt:

    observer.stop()

observer.join()