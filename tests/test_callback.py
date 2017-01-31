import sys
print sys.path
from keras_elastic_callback import ElasticCallback
from elasticsearch import Elasticsearch
from mock import NonCallableMock


def test_data():
    es_mock = NonCallableMock(spec=Elasticsearch)
    callback = ElasticCallback(
        'test_run',
        'test_index',
        event_data={'data_key': 'data_value'},
        es_client=es_mock,
    )

    callback.on_epoch_begin(1)
    es_mock.index.assert_called_once()
    args = es_mock.index.call_args[1]
    assert args['index'] == 'test_index'
    assert args['doc_type'] == 'epoch_begin'
    assert args['body']['event'] == 'epoch_begin'
    assert args['body']['run_name'] == 'test_run'
    assert args['body']['data_key'] == 'data_value'
    assert args['body']['epoch'] == 1


events_names = [
    'train_begin',
    'epoch_begin',
    'batch_begin',
    'batch_end',
    'epoch_end',
    'train_end',
]


def test_all_events():
    es_mock = NonCallableMock(spec=Elasticsearch)
    callback = ElasticCallback(
        'test_run',
        'test_index',
        es_client=es_mock,
    )

    for event in events_names:

        func = getattr(callback, 'on_' + event)
        if 'batch' in event or 'epoch' in event:
            func(1)
        else:
            func()
        args = es_mock.index.call_args[1]
        assert args['doc_type'] == event


def test_buffer():
    es_mock = NonCallableMock(spec=Elasticsearch)
    callback = ElasticCallback(
        'test_run',
        'test_index',
        es_client=es_mock,
        buffer_length=10
    )

    callback.on_batch_begin(1)
    callback.on_batch_end(1)
    es_mock.index.assert_not_called()
