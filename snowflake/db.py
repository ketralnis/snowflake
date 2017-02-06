from collections import namedtuple
import sqlite3

class Database(object):
    def __init__(self, fname):
        self.conn = sqlite3.connect(
            fname,
            # we do our own locking in server mode
            check_same_thread=False)

    def create_schema(self):
        self.conn.executescript("""
            CREATE TABLE samples(
                url PRIMARY KEY
            );

            CREATE TABLE labels(
                label PRIMARY KEY
            );

            CREATE TABLE ratings(
                id INTEGER PRIMARY KEY,
                user_name,
                url,
                label,
                created,
                FOREIGN KEY(url) REFERENCES samples(url),
                FOREIGN KEY(label) REFERENCES labels(label)
            );
            CREATE INDEX i1 ON ratings(url, user_name);

            CREATE TABLE version(
                v PRIMARY KEY
            );
            INSERT INTO version(v) VALUES(1);
        """)

    def verify_schema(self):
        # this will just fail if the table doesn't exist. it's probably good
        # enough
        found = self.conn.execute("SELECT v FROM version")
        if list(found) != [(1,)]:
            raise Exception("This doesn't look like a valid database")

    def import_from(self, fd):
        with self.conn:
            curs = self.conn.cursor()

            curs.executemany(
                """
                    INSERT OR IGNORE INTO samples(url)
                    VALUES(?)
                """,
                ((url,) for url in fd)
            )

    def add_labels(self, labels):
        with self.conn:
            curs = self.conn.cursor()

            curs.executemany(
                """
                    INSERT OR IGNORE INTO labels(label)
                    VALUES(?)
                """,
                ((label,) for label in labels)
            )

    def get_labels(self):
        ret = []

        for (label,) in self.conn.execute("SELECT label FROM labels"):
            ret.append(label)

        ret.sort()
        return ret

    def export(self):
        Entry = namedtuple('Entry', 'url label selected samples')

        # two phases: first grab the winners for each URL and then grab the URLs
        # with no winner
        for url, label, selected, samples in self.conn.execute("""
                SELECT r.url,
                       (SELECT r2.label
                        FROM ratings r2
                        WHERE r.url=r2.url
                        GROUP BY r2.url, r2.label
                        ORDER BY COUNT(r2.label) DESC
                        LIMIT 1) AS winning_label,
                       (SELECT COUNT(r3.label)
                        FROM ratings r3
                        WHERE r.url=r3.url
                        GROUP BY r3.url, r3.label
                        ORDER BY COUNT(r3.label) DESC
                        LIMIT 1) AS count_agreements,
                       COUNT(*) AS num_ratings
                FROM ratings r
                GROUP BY r.url

                UNION ALL

                SELECT ns.url, '(unknown)', 0, 0
                FROM samples ns LEFT JOIN ratings nr ON ns.url=nr.url
                WHERE nr.id IS NULL
            """):
            yield Entry(url, label, selected, samples)

    def export_ratings(self):
        for url, who, label in self.conn.execute("""
                SELECT url, label, user_name
                FROM ratings
                ORDER BY url, label, user_name
            """):
            yield url, label, who

    def get_next(self, user_name=None):
        res = self.conn.execute(
            # ordered as {number without my ratings, number of total ratings}
            """
                SELECT s.url
                FROM samples AS s
                ORDER BY
                    (SELECT COUNT(*)
                     FROM ratings AS r1
                     WHERE s.url=r1.url
                     AND r1.user_name=?) ASC,
                    (SELECT COUNT(DISTINCT r2.user_name)
                     FROM ratings AS r2
                     WHERE s.url=r2.url) ASC,
                    RANDOM() -- break ties
                LIMIT 1
            """, [user_name])

        for (url,) in res:
            # return the URL we found or None
            return url

    def rate(self, url, who, label):
        with self.conn:
            curs = self.conn.cursor()

            curs.execute(
                """
                INSERT INTO ratings(url, label, user_name)
                VALUES (?, ?, ?)
                """,
                [url, label, who])
