from audiophiles.core.rules import RenameRule
from audiophiles.core.tokens import RenameContext, resolve_template
from audiophiles.models import AudioFile


class RenameEngine:
    #Generate new filenames from audio files, templates, and rules

    def rename(
        self,
        audio_file: AudioFile,
        index: int,
        total: int,
        template: str | None = None,
        rules: list[RenameRule] | None = None,
    ) -> str:

    #Generate a new filename without modifying the filesystem

        context = RenameContext(
        audio_file = audio_file,
        index = index,
        total = total,
        )

        if template is not None:
            filename = resolve_template(template, context)
        else:
            filename = audio_file.filename

        if rules is not None:
            for rule in rules:
                filename = rule.apply(filename)

        return filename


    def rename_batch(
        self,
        audio_files: list[AudioFile],
        template: str | None = None,
        rules: list[RenameRule] | None = None,
    ) -> list[str]:

        total = len(audio_files)

        return [
            self.rename(
                audio_file = audio_file,
                index = index,
                total = total,
                template = template,
                rules = rules,
            )
            for index, audio_file in enumerate(audio_files, start = 1)
        ]