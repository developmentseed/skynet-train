import json
import click
from boto3.session import Session
session = Session()

sqs = session.resource('sqs')
s3 = session.client('s3')


def send(queue, messages, dryrun):
    messages = [{'Id': str(i), 'MessageBody': m} for i, m in enumerate(messages)]
    if dryrun:
        print('DRYRUN %s' % json.dumps({'Entries': messages}))
        return
    q = sqs.get_queue_by_name(QueueName=queue)
    resp = q.send_messages(Entries=messages)
    assert len(resp.get('Failed', [])) == 0, str(resp)


def receive(queue):
    q = sqs.get_queue_by_name(QueueName=queue)
    while True:
        for message in q.receive_messages(MaxNumberOfMessages=10, VisibilityTimeout=60):
            yield message


@click.command()
@click.argument('queue_name')
@click.argument('output_bucket')
@click.argument('tileset')
@click.argument('image_tiles')
@click.argument('input', default='-')
@click.option('--tile-url', type=str)
@click.option('--dryrun', is_flag=True, default=False)
def populate(queue_name, output_bucket, tileset, image_tiles, input, tile_url, dryrun):
    """
    Populate the given SQS queue with tasks of the form [bucket, tileset, image_tiles, z, x, y],
    to be consumed by batch_process.py.

    Works well with cover.js. E.g.:

    ./cover.js file.geojson 15 16 | python segnet/queue.py my_queue my_bucket my_tileset "http://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token={MAPBOX_ACCESS_TOKEN}"
    """

    try:
        input = click.open_file(input).readlines()
    except IOError:
        input = [input]
    batch = []
    count = 0
    for tile in input:
        tile = (x, y, z) = json.loads(tile.strip())
        count += 1
        batch.append(json.dumps((output_bucket, tileset, image_tiles, z, x, y)))
        if (len(batch) == 10):
            send(queue_name, batch, dryrun)
            batch = []

    if len(batch) > 0:
        send(queue_name, batch, dryrun)

    if not tile_url:
        tile_url = 'https://%s.s3.amazonaws.com/%s/{z}/{x}/{y}.png' % (output_bucket, tileset)
    tilejson = json.dumps({
        'tilejson': '2.0.0',
        'tiles': [tile_url]
    })
    key = '%s/index.json' % tileset
    click.echo('%s tiles queued. Pushing TileJSON to %s/%s' % (count, output_bucket, tileset))
    click.echo(tilejson)
    if not dryrun:
        s3.put_object(Body=tilejson, Bucket=output_bucket, Key=key, ContentType='application/json')


if __name__ == '__main__':
    populate()
