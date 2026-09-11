import re
from dataclasses import dataclass
from audiophiles.models import AudioFile

TOKEN_PATTERN = re.compile(r"\$[a-zA-Z]+(?::[0-9]+)?")

@dataclass(frozen=True)
class RenameContext:
    #Context used to resolve rename tokens for an audio file

    audio_file: AudioFile
    index: int
    total: int

    @property
    def filename(self) -> str:
        #return the complete filename, including extension
        return self.audio_file.filename

    @property
    def stem(self) -> str:
        #return filename without extension
        return self.audio_file.stem
    
    @property
    def extension(self) -> str:
        #return file extension, including the leading period
        return self.audio_file.extension

    @property
    def folder(self) -> str:
        #return the containing folder name
        return self.audio_file.folder.name


def resolve_token(token: str, context: RenameContext) -> str:
    #resolve a single rename token using the provided context

    tokens = {
        "$filename": context.filename,
        "$stem": context.stem,
        "$extension": context.extension,
        "$folder": context.folder,
        "$index": str(context.index),
    }

    if token in tokens:
        return tokens[token]

    if token.startswith("$index:"):
        width_text = token.split(":", 1)[1]

        if not width_text.isdigit():
            raise ValueError(f"Invalid index format: {token}")

        width = int(width_text)

        if width <= 0:
            raise ValueError(f"Invalid index format: {token}")

        return f"{context.index:0{width}d}"

    raise ValueError(f"Unknown rename token: {token}")

def resolve_template(template: str, context: RenameContext) -> str:
    #Resolve all rename tokens contained in a template

    def replace_token(match: re.Match[str]) -> str:
        return resolve_token(match.group(0), context)

    return TOKEN_PATTERN.sub(replace_token, template)
