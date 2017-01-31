import argparse

from snowflake.db import Database
from snowflake.web.app import make_app

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--db', required=True)

    parser.add_argument('--init', action="store_true", default=False)

    parser.add_argument('--labels',
                        help='add some labels as options')
    parser.add_argument('--import', dest='import_',
                        help='import samples from the given file (or -)')
    parser.add_argument('--export',
                        help="export completed adjudications",
                        action="store_true", default=False)
    parser.add_argument('--export-ratings',
                        help="export all individual ratings",
                        action="store_true", default=False)

    parser.add_argument('--get-next', default=False)

    parser.add_argument('--server', action='store_true', default=False)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=8080, type=int)
    parser.add_argument('--debug', action='store_true', default=False)

    args = parser.parse_args()

    db = Database(args.db)

    if args.init:
        db.create_schema()
    else:
        db.verify_schema()

    if args.import_:
        if args.import_ == '-':
            fd = sys.stdin
        else:
            fd = open(args.import_)

        lines = fd
        lines = (line.rstrip('\n') for line in lines)
        lines = (line for line in lines if line)

        db.import_from(lines)

    if args.labels:
        labels = args.labels.split(',')
        print 'Adding labels:', ', '.join(labels)
        db.add_labels(labels)

    if args.export:
        for url, label, selected, samples in db.export():
            print '%s\t%s\t%d\t%d' % (url, label, selected, samples)

    if args.export_ratings:
        for url, label, who in db.export_ratings():
            print "%s\t%s\t%s" % (url, who, label)

    if args.get_next:
        print db.get_next(args.get_next)

    if args.server:
        app = make_app(db=db, debug=args.debug)
        app.run(host=args.host, port=args.port,
                debug=args.debug)


if __name__ == '__main__':
    main()