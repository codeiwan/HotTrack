import datetime
import json
from io import BytesIO
from typing import Literal
from urllib.request import urlopen

import pandas as pd

from django.db.models import QuerySet, Q
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView

from hottrack.models import Song
from hottrack.utils.cover import make_cover_image


def index(request: HttpRequest, release_date: datetime.date = None) -> HttpResponse:
    query = request.GET.get("query", "").strip()

    song_qs: QuerySet[Song] = Song.objects.all()

    if release_date:
        song_qs = song_qs.filter(release_date=release_date)

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


song_detail = DetailView.as_view(
    model=Song,
    slug_field="melon_uid",
    slug_url_kwarg="melon_uid",
)


def export(request, format: Literal["csv", "xlsx"]):
    song_qs = Song.objects.all()
    df = pd.DataFrame(data=song_qs.values())

    export_file = BytesIO()

    if format == 'csv':
        content_type = "text/csv"
        filename = "hottrack.csv"
        df.to_csv(path_or_buf=export_file, index=False, encoding="utf-8-sig")
    elif format == 'xlsx':
        content_type = "application/vnd.ms-excel"
        filename = "hottrack.xlsx"
        df.to_excel(excel_writer=export_file, index=False)
    else:
        return HttpResponseBadRequest(f"Invalid format : {format}")

    response = HttpResponse(content=export_file.getvalue(), content_type=content_type)
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)

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
