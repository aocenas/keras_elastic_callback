from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from datetime import datetime
from keras.callbacks import Callback
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import numpy as np


class ElasticCallback(Callback):
    """
    Sends all data to elasticsearch.
    """
    def __init__(
            self,
            run_name,
            index_name='keras',
            event_data=None,
            url=None,
            es_client=None,
            buffer_length=1,
    ):
        """
        :param str run_name: Name of the run that can be searched for.
        :param str index_name: Name of index in elasticsearch. Must be lowercase
        and cannot contain special characters.
        :param Dict event_data: Additional data that will be merged each each
        event.
        :param str url: Elasticsearch url <host>[:<port>]
        :param object es_client: Elasticsearch client
        :param int buffer_length: Length of event buffer, before events are sent
        to Elasticsearch. If length is 1, event is sent after and before
        each batch, which can slow down learning. If buffer_length is 0, events
        are flushed only on epoch end. If buffer_length is > 1, number of events
        will be buffered before flushed, but still everything is flushed on
        epoch end.
        """
        super(ElasticCallback, self).__init__()
        if es_client:
            self.es = es_client
        else:
            self.es = Elasticsearch([url])
        self.index = index_name
        self.run_name = run_name
        self.data = event_data or {}
        self.batch_start_time = None
        self.epoch_start_time = None
        self.event_buffer = []
        self.buffer_length = buffer_length

    def on_train_begin(self, logs={}):
        self._index(
            'train_begin',
            logs,
        )

    def on_epoch_begin(self, epoch, logs={}):
        self.epoch_start_time = datetime.now()
        self._index(
            'epoch_begin',
            logs,
            epoch=epoch,
        )

    def on_batch_begin(self, batch, logs={}):
        self.batch_start_time = datetime.now()
        self._add_to_queue(
            'batch_begin',
            logs,
        )

    def on_batch_end(self, batch, logs={}):
        self._add_to_queue(
            'batch_end',
            logs,
            duration=(datetime.now() - self.batch_start_time).seconds,
        )

    def on_epoch_end(self, epoch, logs={}):
        self._flush_queue()
        self._index(
            'epoch_end',
            logs,
            duration=(datetime.now() - self.epoch_start_time).seconds,
            epoch=epoch,
        )

    def on_train_end(self, logs={}):
        self._index('train_end', logs)

    def _add_to_queue(self, doc_type, logs, **kw):
        if self.buffer_length == 1:
            self._index(
                doc_type,
                logs,
                **kw
            )
        else:
            self.event_buffer.append((
                doc_type,
                self._create_event_body(doc_type, logs, **kw)
            ))

            if len(self.event_buffer) == self.buffer_length:
                self._flush_queue()

    def _flush_queue(self):
        if len(self.event_buffer):
            bulk(self.es, self._map_actions(self.event_buffer))
            self.event_buffer = []

    def _map_actions(self, events):
        def mapper(event):
            return {
                '_op_type': 'index',
                '_index': self.index,
                '_type': event[0],
                '_source': event[1],
            }
        return map(mapper, events)

    def _index(self, doc_type, logs, **kw):
        self.es.index(
            index=self.index,
            doc_type=doc_type,
            body=self._create_event_body(doc_type, logs, **kw),
        )

    def _create_event_body(self, doc_type, logs, **kw):
        body = dict(
            timestamp=datetime.utcnow().isoformat(),
            event=doc_type,
            run_name=self.run_name,
            **self._convert_np_arrays(logs)
        )
        body.update(kw)
        body.update(self.data)
        return body

    @staticmethod
    def _convert_np_arrays(data):
        """
        Convert numpy ndarrays in a dictionary to list, so it can be serialized
        to JSON.
        """
        return {
            k: v.tolist() if type(v) == np.ndarray else v
            for k, v
            in data.items()
        }