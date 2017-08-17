#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    所有 Model 的基类 MongoDoc
'''
import _env # noqa
import datetime

from mongokit import Document, connection as mongo_con, Connection
from mongokit.document import DocumentProperties
from data.config import MongoConfig
from bson.objectid import ObjectId
from yajl import dumps


class CallableMixin(object):
    """
    brings the callable method to a Document. usefull for the connection's
    register method
    """
    def __call__(self, doc=None, gen_skel=False, lang='en', fallback_lang='en'):
        return self._obj_class(
            doc=doc,
            gen_skel=gen_skel,
            collection=self.collection,
            lang=lang,
            fallback_lang=fallback_lang
        )


mongo_con.CallableMixin = CallableMixin
mongo = Connection(host=MongoConfig.mongo_uri)


class MetaDoc(DocumentProperties):
    def __new__(cls, name, bases, attrs):
        new_cls = super(MetaDoc, cls).__new__(cls, name, bases, attrs)
        if bases[0] is not Document:

            new_cls.__mongo__ = mongo
            if not new_cls.__name__.startswith('Callable'):
                new_cls.__collection__ = attrs.get('__collection__') or name
                new_cls = mongo.register(new_cls)
                new_cls = getattr(mongo, name)
            else:
                new_cls._protected_field_names.append("_collection")
                _ = getattr(new_cls.__mongo__, new_cls.__database__)
                _ = getattr(_, new_cls.__collection__)
                new_cls._collection = _

        return new_cls


class MongoDoc(Document):
    __metaclass__ = MetaDoc
    __database__ = MongoConfig.db
    use_dot_notation = True  # 允许使用链式调用查看 value
    use_autorefs = False
    skip_validation = True

    def __init__(self, doc={}, gen_skel=None, *args, **kwargs):
        """
            gen_skel为 True 时设置default value 否则不设置
        """
        if doc is None:
            doc = dict()
        else:
            if isinstance(doc, JsOb):
                doc = doc.__dict__
        super(MongoDoc, self).__init__(doc, *args, **kwargs)
        for i in self.structure:
            if i not in doc:
                self[i] = None

        if gen_skel:
            if self.default_values:
                self._set_default_fields(self, self.structure)

    def upsert(self, spec, multi=False, update_self=False):
        """
            根据条件先查询是否有对应 document
            如果有则更新 如果没有则创建
        """
        if isinstance(spec, basestring):
            spec = {'_id': ObjectId(spec)}
        update = dict((k, v) for k, v in self.iteritems() if v is not None)
        update.update(spec)
        res = self.collection.update(
            spec,
            {'$set': update},
            upsert=True,
            multi=multi
        )

        print "res>>>>>>>>: {}".format(res)
        if update_self:
            d = self.cllection.find_one(spec)
            for k, v in d.iteritems():
                self[k] = v

        return self

    @classmethod
    def update(cls, spec, data, multi=False, **kwargs):
        cls._collection.update(spec, data, multi=multi, **kwargs)

    def save(self, *args, **kwargs):
        if '_id' in self:
            _id = self['_id']
            if isinstance(_id, basestring):
                self['id'] = ObjectId(_id)

        super(MongoDoc, self).save(*args, **kwargs)
        return self

    @classmethod
    def count(cls, *args, **kwargs):
        return cls._collection.find(*args, **kwargs).count()

    @classmethod
    def find(cls, *args, **kwargs):
        result = []
        for i in cls._collection.find(*args, **kwargs):
            i['_id'] = str(i['_id'])
            result.append(i)
        return map(lambda doc: cls(doc, collection=cls._collection), result)

    @classmethod
    def find_one(cls, spec_or_id=None, *args, **kwargs):
        if isinstance(spec_or_id, basestring):
            spec_or_id = ObjectId(spec_or_id)

        o = cls._collection.find_one(spec_or_id, *args, **kwargs)
        if o:
            o['_id'] = str(o['_id'])
            return cls(o, collection=cls._colletion)

    def delete(self):
        collection = getattr(self, '_collection', self.collection)
        collection.remove({'_id': ObjectId(self['_id'])})

    @classmethod
    def remove(cls, spec_or_id, safe=None, multi=True, **kwargs):
        if isinstance(spec_or_id, basestring):
            spec_or_id = ObjectId(spec_or_id)

        if spec_or_id:
            cls._collection.remove(spec_or_id=spec_or_id, safe=safe, multi=multi, **kwargs)

    @classmethod
    def drop(cls):
        cls._collection.drop()

    @classmethod
    def iterdoc(cls, *args, **kwargs):
        skip = 0
        limit = 5000
        while True:
            kwargs.update(dict(skip=skip, limit=limit))
            result = cls.find(*args, **kwargs)
            if not result:
                break
            for doc in result:
                yield doc
            skip += limit

    def to_dict(self):
        d = dict(self)

        for k, v in d.iteritems():
            if k == '_id':
                d['_id'] = str(v) if v else ''

            if isinstance(v, datetime.datetime):
                d[k] = v.strftime('%Y-%m-%d %H:%M:%S')

        return d

    @classmethod
    def insert_many(cls, li):
        return cls._collection.insert(li)


class JsOb(object):
    def __init__(self, *args, **kwds):
        for i in args:
            self.__dict__.update(args)
        self.__dict__.update(kwds)

    def __getattr__(self, name):
        return self.__dict__.get(name, '')

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            del self.__dict__[name]

    def __repr__(self):
        return self.__dict__.__repr__()

    __getitem__ = __getattr__
    __delitem__ = __delattr__
    __setitem__ = __setattr__

    def __len__(self):
        return self.__dict__.__len__()

    def __iter__(self):
        return self.__dict__.iteritems()

    def __contains__(self, name):
        return self.__dict__.__contains__(name)

    def __str__(self):
        return dumps(self.__dict__)


if __name__ == '__main__':
    class TestModel(MongoDoc):
        __collection__ = 'test_model'

        structure = dict(
            name=basestring,
            age=int,
            info=dict()
        )
        indexs = [
            {'field': 'name'},
        ]
    TestModel({'name': 'Jack Chen', 'age': 18, 'info': {'addr': '北京'}}).upsert({})
