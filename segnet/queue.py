import json
import click
from boto3.session import Session
import mercantile
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
@click.option('--zoom', type=int)
@click.option('--min-zoom', type=int)
@click.option('--max-zoom', type=int)
@click.option('--bbox', nargs=4, type=float, required=True)
@click.option('--tile-url', type=str)
@click.option('--dryrun', is_flag=True, default=False)
def populate(queue_name, output_bucket, tileset, zoom, min_zoom, max_zoom, bbox, tile_url, dryrun):
    batch = []
    count = 0
    (w, s, e, n) = bbox
    if not min_zoom:
        min_zoom = zoom
    if not max_zoom:
        max_zoom = zoom
    for z in range(min_zoom, max_zoom + 1):
        for tile in mercantile.tiles(w, s, e, n, [z], truncate=False):
            count += 1
            batch.append(json.dumps((output_bucket, tileset, z, tile.x, tile.y)))
            if (len(batch) == 10):
                send(queue_name, batch, dryrun)
                batch = []

    if len(batch) > 0:
        send(queue_name, batch, dryrun)

    if not tile_url:
        tile_url = 'https://%s.s3.amazonaws.com/%s/{z}/{x}/{y}.png' % (output_bucket, tileset)
    tilejson = json.dumps({
        'tilejson': '2.0.0',
        'tiles': [tile_url],
        'minzoom': min_zoom,
        'maxzoom': max_zoom,
        'bounds': bbox
    })
    key = '%s/index.json' % tileset
    click.echo('%s tiles queued. Pushing TileJSON to %s/%s' % (count, output_bucket, tileset))
    click.echo(tilejson)
    if not dryrun:
        s3.put_object(Body=tilejson, Bucket=output_bucket, Key=key, ContentType='application/json')


if __name__ == '__main__':
    populate()
