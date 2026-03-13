from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

ROOT_DIR = Path(__file__).resolve().parents[2]
PACKAGES_DIR = ROOT_DIR / "packages"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from memory_config.logging import configure_logging
from memory_config.settings import get_settings
from memory_core.db import SessionLocal
from memory_core.indexer import VaultIndexer
from memory_vectorstore.embeddings import build_embedding_provider

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("indexer")


class VaultEventHandler(FileSystemEventHandler):
    def __init__(self, queue: asyncio.Queue[str], memory_root: Path) -> None:
        self.queue = queue
        self.memory_root = memory_root

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".md":
            return
        relative = str(path.relative_to(self.memory_root))
        try:
            self.queue.put_nowait(relative)
        except asyncio.QueueFull:
            logger.warning("Indexer queue full; dropping event for %s", relative)


async def consume_events(queue: asyncio.Queue[str], indexer: VaultIndexer) -> None:
    while True:
        relative_path = await queue.get()
        async with SessionLocal() as db:
            try:
                changed = await indexer.index_relative_path(db, relative_path)
                logger.info("Processed change path=%s changed=%s", relative_path, changed)
            except Exception:
                logger.exception("Failed to process file change: %s", relative_path)
        queue.task_done()


async def run_once(indexer: VaultIndexer) -> None:
    async with SessionLocal() as db:
        await indexer.rebuild(db)


async def main() -> None:
    embedding_provider = build_embedding_provider()
    indexer = VaultIndexer(settings=settings, embedding_provider=embedding_provider)

    await run_once(indexer)

    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=2048)
    handler = VaultEventHandler(queue=queue, memory_root=indexer.workspace.root_path)
    observer = Observer()
    for watch_root in indexer.workspace.iter_index_roots():
        observer.schedule(handler, str(watch_root), recursive=True)
    observer.start()

    logger.info("Watching memory roots: %s", ", ".join(str(path) for path in indexer.workspace.iter_index_roots()))
    try:
        await consume_events(queue, indexer)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    asyncio.run(main())
