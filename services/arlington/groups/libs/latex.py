import os
import subprocess
import tempfile
from django.conf import settings

from arlington.settings import BASE_DIR
from groups.models import Document


class Renderer(object):
    _params = ["-output-format=pdf", "-shell-escape", "-interaction=nonstopmode"]

    def __init__(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        self._temp_file = tempfile.NamedTemporaryFile(dir=self._temp_dir.name, delete=False)
        self._timeout = settings.LATEX_TIMEOUT
        self._latex_binary = settings.LATEX_BINARY

    def _build_command(self, filename):
        command = [self._latex_binary]
        command += self._params
        command.append("-output-directory={}".format(self._temp_dir.name))
        command.append(filename)
        return command

    def render(self, text: str):
        self._temp_file.write(text.encode())
        self._temp_file.close()
        command = self._build_command(self._temp_file.name)
        res = subprocess.call(command, stdout=subprocess.DEVNULL, timeout=self._timeout)
        return res

    def output_filename(self):
        return self._temp_file.name + '.pdf'

    def output_file(self):
        return open(self.output_filename(), 'rb')

    def output_bytes(self):
        with open(self.output_filename(), 'rb') as f:
            return f.read()

    def clean(self):
        self._temp_dir.cleanup()


class DocumentPresenter:
    @staticmethod
    def present(document: Document):
        filename = os.path.join(BASE_DIR, 'groups/libs/template.tex')
        with open(filename, 'r') as f:
            data = f.read()
            data = data % (document.title, document.text)
            return data
