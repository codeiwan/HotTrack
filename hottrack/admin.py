from django.contrib import admin
from django.utils.html import format_html

from .models import Song
from .utils.melon import get_likes_dict


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    search_fields = ["name", "artist_name", "album_name"]
    list_display = [
        "cover_image",
        "name",
        "artist_name",
        "album_name",
        "genre",
        "like_count",
        "release_date",
    ]
    list_filter = ["genre", "release_date"]
    actions = ["update_like_count"]

    @staticmethod
    def cover_image(song) -> str:
        return format_html('<img src="{}" style="width: 50px;" />', song.cover_url)

    def update_like_count(self, request, queryset):
        melon_uid_list = queryset.values_list("melon_uid", flat=True) 
        likes_dict = get_likes_dict(melon_uid_list)
        print("likes_dict :", likes_dict)

        # 일괄 UPDATE 쿼리
        changed_count = 0
        for song in queryset:
            if song.like_count != likes_dict[song.melon_uid]:
                song.like_count = likes_dict[song.melon_uid]
                changed_count += 1

        Song.objects.bulk_update(
            queryset,
            fields=["like_count"],
        )

        self.message_user(request, f"{changed_count} 곡의 좋아요 갱신 완료")
