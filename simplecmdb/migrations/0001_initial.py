# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'simplecmdb_project', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, primary_key=True)),
            ('contact', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'simplecmdb', ['Project'])

        # Adding model 'IDC'
        db.create_table(u'simplecmdb_idc', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, primary_key=True)),
        ))
        db.send_create_signal(u'simplecmdb', ['IDC'])

        # Adding model 'AssetType'
        db.create_table(u'simplecmdb_assettype', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, primary_key=True)),
        ))
        db.send_create_signal(u'simplecmdb', ['AssetType'])

        # Adding model 'AssetField'
        db.create_table(u'simplecmdb_assetfield', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
        ))
        db.send_create_signal(u'simplecmdb', ['AssetField'])

        # Adding M2M table for field assettype on 'AssetField'
        m2m_table_name = db.shorten_name(u'simplecmdb_assetfield_assettype')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('assetfield', models.ForeignKey(orm[u'simplecmdb.assetfield'], null=False)),
            ('assettype', models.ForeignKey(orm[u'simplecmdb.assettype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['assetfield_id', 'assettype_id'])

        # Adding model 'Asset'
        db.create_table(u'simplecmdb_asset', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, primary_key=True)),
            ('assettype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['simplecmdb.AssetType'])),
            ('idc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['simplecmdb.IDC'])),
        ))
        db.send_create_signal(u'simplecmdb', ['Asset'])

        # Adding M2M table for field project on 'Asset'
        m2m_table_name = db.shorten_name(u'simplecmdb_asset_project')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('asset', models.ForeignKey(orm[u'simplecmdb.asset'], null=False)),
            ('project', models.ForeignKey(orm[u'simplecmdb.project'], null=False))
        ))
        db.create_unique(m2m_table_name, ['asset_id', 'project_id'])

        # Adding model 'AssetFieldValue'
        db.create_table(u'simplecmdb_assetfieldvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['simplecmdb.Asset'])),
            ('assetinfo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['simplecmdb.AssetField'])),
            ('fieldvalue', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'simplecmdb', ['AssetFieldValue'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table(u'simplecmdb_project')

        # Deleting model 'IDC'
        db.delete_table(u'simplecmdb_idc')

        # Deleting model 'AssetType'
        db.delete_table(u'simplecmdb_assettype')

        # Deleting model 'AssetField'
        db.delete_table(u'simplecmdb_assetfield')

        # Removing M2M table for field assettype on 'AssetField'
        db.delete_table(db.shorten_name(u'simplecmdb_assetfield_assettype'))

        # Deleting model 'Asset'
        db.delete_table(u'simplecmdb_asset')

        # Removing M2M table for field project on 'Asset'
        db.delete_table(db.shorten_name(u'simplecmdb_asset_project'))

        # Deleting model 'AssetFieldValue'
        db.delete_table(u'simplecmdb_assetfieldvalue')


    models = {
        u'simplecmdb.asset': {
            'Meta': {'object_name': 'Asset'},
            'assettype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['simplecmdb.AssetType']"}),
            'idc': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['simplecmdb.IDC']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['simplecmdb.Project']", 'symmetrical': 'False'})
        },
        u'simplecmdb.assetfield': {
            'Meta': {'object_name': 'AssetField'},
            'assettype': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['simplecmdb.AssetType']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        },
        u'simplecmdb.assetfieldvalue': {
            'Meta': {'object_name': 'AssetFieldValue'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['simplecmdb.Asset']"}),
            'assetinfo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['simplecmdb.AssetField']"}),
            'fieldvalue': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'simplecmdb.assettype': {
            'Meta': {'object_name': 'AssetType'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'})
        },
        u'simplecmdb.idc': {
            'Meta': {'object_name': 'IDC'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'})
        },
        u'simplecmdb.project': {
            'Meta': {'object_name': 'Project'},
            'contact': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'})
        }
    }

    complete_apps = ['simplecmdb']