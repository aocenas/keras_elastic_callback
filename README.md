##Callback for Keras that sends all data to Elasticsearch.

If you want some visualisations of your training when using Theano,
or you want some more custom visualisation, for exemple with Kibana.

####install:
```bash
pip install keras_elastic_callback
```


####usage:
```python

model.fit(X, Y,
    callbacks=[
        ElasticCallback(
            # Run name, which should be unique so you can identifiy
            # your runs in the elasticsearch
            'unique_run_name',
            
            # Name of the index where the events are sent. 
            index_name='keras',
            
            # Dict of custom data that will be sent with every event.
            event_data=None,
            
            # Url to your elasticsearch server
            url='localhost:9200',
            
            # Instead of url you can pass existing elastic client.
            es_client=None,
            
            # Number of events that will be buffered before they are sent
            # to Elastic. Only for batch_begin and batch_end. If set to 0
            # events are sent only on epoch_end. If 1 they are sent realtime
            # but that can affect performance.
            buffer_length=0
        ),
    ]
)
```

####running elastic and kibana
If you have docker and docker compose you can use docker-compose.yml to run
both elastic and kibana.
```bash
cd keras_elastic_callback
docker-compose up
```
