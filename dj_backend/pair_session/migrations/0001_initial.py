# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'pair_room'
        db.create_table(u'pair_session_pair_room', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room_name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'pair_session', ['pair_room'])


    def backwards(self, orm):
        # Deleting model 'pair_room'
        db.delete_table(u'pair_session_pair_room')


    models = {
        u'pair_session.pair_room': {
            'Meta': {'object_name': 'pair_room'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'room_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['pair_session']