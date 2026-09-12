from typing import Protocol


class RenameRule(Protocol):
    #Interface implemented by filename transformation rules

    def apply(self, filename: str) -> str:
        #Transform a filename and return the result
        ...


class PrefixRule:
    #Add a prefix to a filename

    def __init__(self, prefix: str):
        self.prefix = prefix

    def apply(self, filename: str) -> str:
        #Return filename with the prefix added

        return f"{self.prefix}{filename}"


class SuffixRule:
    #Add a suffix to a filename

    def __init__(self, suffix: str):
        self.suffix = suffix

    def apply(self, filename: str) -> str:
        #Return filename with the suffix added before the extension

        if "." not in filename:
            return f"{filename}{self.suffix}"

        #rsplit in case filenames contain more than one "."
        stem, extension = filename.rsplit(".", 1)

        #adding back one "." here
        return f"{stem}{self.suffix}.{extension}"


class ReplaceRule:
    #Replace occurrences of text within a filename

    def __init__(self, old: str, new: str):
        self.old = old
        self.new = new

    def apply(self, filename: str) -> str:
        #Return the filname with matching text replaced

        return filename.replace(self.old, self.new)


class RemoveRule:
    #Remove occurrences of text from a filename

    def __init__(self, text: str):
        self.text = text

    def apply(self, filename: str) -> str:
        #Return the filename with matching text removed

        return filename.replace(self.text, "")