from random import choices
import string
from os.path import isfile
from celery import shared_task
from django.core.files import File
from groups.libs.latex import Renderer, DocumentPresenter
from groups.models import Document


@shared_task
def render_document(document_id):
    document = Document.objects.get(id=document_id)
    latex = Renderer()
    latex.render(DocumentPresenter.present(document))
    name = ''.join(choices(string.ascii_letters + string.digits, k=12))
    if isfile(latex.output_filename()):
        document.rendered_file.save(name + ".pdf", File(latex.output_file()))
        document.save()
    else:
        raise Exception("Can't render latex")
    latex.clean()
