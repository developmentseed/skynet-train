import json
import argparse
from boto3.session import Session
import mercantile
session = Session()

sqs = session.resource('sqs')


def send(queue, messages, dryrun):
    messages = [{'Id': str(i), 'MessageBody': m} for i, m in enumerate(messages)]
    if dryrun:
        print(json.dumps({'Entries': messages}))
        return
    q = sqs.get_queue_by_name(QueueName=queue)
    resp = q.send_messages(Entries=messages)
    assert len(resp.get('Failed', [])) == 0, str(resp)


def receive(queue, **kwargs):
    q = sqs.get_queue_by_name(QueueName=queue)
    return q.receive_messages(**kwargs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('queue_name', type=str)
    parser.add_argument('z', type=int)
    parser.add_argument('w', type=float)
    parser.add_argument('s', type=float)
    parser.add_argument('e', type=float)
    parser.add_argument('n', type=float)
    parser.add_argument('--dryrun', action='store_true', default=False)
    args = parser.parse_args()
    batch = []
    for tile in mercantile.tiles(args.w, args.s, args.e, args.n, [args.z], truncate=False):
        batch.append(json.dumps((args.z, tile.x, tile.y)))
        if (len(batch) == 10):
            send(args.queue_name, batch, args.dryrun)
            batch = []

    if len(batch) > 0:
        send(args.queue_name, batch, args.dryrun)
