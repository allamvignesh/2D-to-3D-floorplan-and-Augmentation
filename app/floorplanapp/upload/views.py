from django.shortcuts import redirect, render
from .models import Document, HouseModel
from .forms import DocumentForm
import os
from django.conf import settings
from .wallDetect import fetch


def my_view(request):
    openModel = False
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            name = newdoc.docfile.name
            fetch(name)
            newdoc.docfile.delete()
            newdoc.delete()

            openModel = True

    else:
        form = DocumentForm()

    documents = list_plans()

    context = {'documents': documents, 'form': form, 'openModel': openModel}
    return render(request, 'index.html', context)


def list_plans():
    Mdir = os.path.join(settings.MODELS_ROOT)
    houses = [
        os.path.join(settings.MEDIA_URL, 'models//', file)
        for file in os.listdir(Mdir)
        if file.endswith(('.glb'))
    ]
    return sorted(houses, key=lambda x: int(x.split("model")[-1].split(".")[0]))[::-1]