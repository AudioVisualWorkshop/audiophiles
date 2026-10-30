from audiophiles.history.models import RenameHistoryEntry

class HistoryManager:
    #Store and retrieve rename history entries

    def __init__(self) -> None:
        self._entries: list[RenameHistoryEntry] = []

    def record(self, entry: RenameHistoryEntry) -> None:
        #Add a completed rename operation to history
        self._entries.append(entry)

    def get_all(self) -> list[RenameHistoryEntry]:
        #Return all history entries, oldest first
        return list(self._entries)

    def get_latest(self) -> RenameHistoryEntry | None:
        #Return the most recently recorded entry, if available
        if not self._entries:
            return None

        return self._entries[-1]

    def clear(self) -> None:
        #Clear all stored history entries
        self._entries.clear()