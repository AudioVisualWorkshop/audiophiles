from audiophiles.core.rename_plan import RenameOperation, RenamePlan
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


    def create_plan(
        self,
        audio_files: list[AudioFile],
        template: str | None = None,
        rules: list[RenameRule] | None = None,
    ) -> RenamePlan:
        #Create a rename plan without modifying the filesystem

        new_filenames = self.rename_batch(
            audio_files = audio_files,
            template = template,
            rules = rules
        )

        operations = [
            RenameOperation(
                source = audio_file.path,
                destination = audio_file.path.with_name(new_filename),
            )
            for audio_file, new_filename in zip(audio_files, new_filenames)
        ]

        return RenamePlan(operations=operations)