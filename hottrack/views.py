import json
from urllib.request import urlopen

from io import BytesIO
import pandas as pd

from django.db.models import QuerySet, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from hottrack.utils.cover import make_cover_image

from hottrack.models import Song


def index(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("query", "").strip()

    song_qs: QuerySet[Song] = Song.objects.all()

    if query:
        song_qs = song_qs.filter(
            Q(name__icontains=query)
            | Q(artist_name__icontains=query)
            | Q(album_name__icontains=query)
        )

    return render(
        request=request,
        template_name="hottrack/index.html",
        context={
            "song_list": song_qs,
            "query": query,
        },
    )


def export_csv(request):
    song_qs = Song.objects.all()
    df = pd.DataFrame(data=song_qs.values())

    export_file = BytesIO()

    df.to_csv(export_file, index=False, encoding="utf-8-sig")
    
    response = HttpResponse(content=export_file.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="hottrack.csv"'

    return response


def cover_png(request, pk):
    # 최대값 512, 기본값 256
    canvas_size = min(512, int(request.GET.get("size", 256)))

    song = get_object_or_404(Song, pk=pk)

    cover_image = make_cover_image(
        song.cover_url, song.artist_name, canvas_size=canvas_size
    )

    # param fp : filename (str), pathlib.Path object or file object
    # image.save("image.png")
    response = HttpResponse(content_type="image/png")
    cover_image.save(response, format="png")

    return response
