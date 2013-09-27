from django.db import models

class PairRoom(models.Model):
    room_name = models.CharField(db_index=True, max_length=255)
    language = models.CharField(max_length=50)