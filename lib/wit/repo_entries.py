from typing import List, Optional
from pathlib import Path
import json


# The intent of RepoEntry and List[RepoEntry] is that no other
# parts of the codebase knows that json is used as the on-disk format, or know
# any of the field names.


class RepoEntry:

    def __init__(self, workspace_name, revision, remote_path, remote_name, message):
        # The path to checkout at within the workspace.
        # JSON field name is 'name'.
        self.workspace_name = workspace_name

        # Desired revision that exists in the history of the below remote.
        # JSON field name is 'commit'
        self.revision = revision

        # Url (or local fs path) for git to clone/fetch/push.
        # JSON field name is 'source'
        self.remote_path = remote_path

        # Name assigned to the remote within the repository checkout.
        # Optional. JSON field name is 'remote_name'
        self.remote_name = remote_name

        # A comment to leave in any serialized artifacts.
        # Optional. JSON field name is '//'
        self.message = message

    def __repr__(self):
        return str(self.__dict__)

    def serialized_names(self) -> dict:
        d = {
            "name": self.workspace_name,
            "commit": self.revision,
            "source": self.remote_path,
        }
        if self.remote_name and len(self.remote_name) > 0:
            d["remote_name"] = self.remote_name
        if self.message and len(self.message) > 0:
            d["//"] = self.message
        return d

    @staticmethod
    def from_serialized_names(data: dict):
        return RepoEntry(data["name"],
                         data["commit"],
                         data["source"],
                         data.get("remote_name"), # optional
                         data.get("//"))          # optional

    def to_dependency(self):
        from .dependency import Dependency
        return Dependency(self.workspace_name, self.remote_path, self.revision, self.message)

    def to_package(self):
        from .package import Package
        pkg = Package(self.workspace_name, [])
        pkg.set_source(self.remote_path)
        pkg.revision = self.revision
        return pkg


# Utilities for List[RepoEntry]
# maybe rename to RepoEntries
class RepoEntries:
    @staticmethod
    def parse_repo_entries(text: str) -> List[RepoEntry]:
        # TODO still read old format from lockfile
        #try:
        fromtext = json.loads(text)
        #except
        #   pass

        out = []
        for entry in fromtext:
            out.append(RepoEntry.from_serialized_names(entry))
        return out

    @staticmethod
    def write_repo_entries(path: Path, entries: List[RepoEntry]):
        dict_data = [e.serialized_names() for e in entries]
        json_data = json.dumps(dict_data, sort_keys=True, indent=4) + "\n"
        path.write_text(json_data)

    @staticmethod
    def read_repo_entries(path: Path) -> List[RepoEntry]:
        text = path.read_text()
        return RepoEntries.parse_repo_entries(text)

    @staticmethod
    def to_manifest(entries: List[RepoEntry]):
        from .manifest import Manifest
        deps = [e.to_dependency() for e in entries]
        return Manifest(deps)

    @staticmethod
    def to_lock(repos: List[RepoEntry]):
        from .lock import LockFile
        return LockFile([e.to_package() for e in entries])


if __name__ == '__main__':
    entries = RepoEntries.read_repo_entries(Path("./wit-lock.json"))
    print(entries)
