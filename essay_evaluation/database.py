import neo4j
import atexit

# this variable holds the database session for the whole project.
# you can get it by calling get_session()
_db = None


class DatabaseInconsistency(Exception):
    pass


def get_driver(url='bolt://localhost:7687', username='neo4j', password='elia.2018'):
    """
    returns the database session. If there's not connection it will be created.
    :return:Driver
    """
    global _db
    if _db is None:
        _db = neo4j.GraphDatabase.driver(url, auth=(username, password))
    assert isinstance(_db, neo4j.Driver)
    return _db


def get_collocation_metric(tx, collocations):
    # we first convert the list of Collocation objects to a dict in order to be able to be sent to the database
    lst_converted = [{'lempos1': col.lempos1, 'lempos2': col.lempos2, 'type': col.type} for col in collocations]
    form = """  UNWIND {batch} as row
                OPTIONAL MATCH (w:Word:EN{lempos: row.lempos1})<-[r:COLLOCATES_WITH{type: row.type}]-(c:Word:EN{lempos: row.lempos2})
                RETURN w.lempos AS lempos1, c.lempos AS lempos2, r.metric AS metric, row.lempos1 AS input_lempos1,
                       row.type AS input_type, row.lempos2 AS input_lempos2
    """
    result = tx.run(form, {'batch': lst_converted})
    for idx, item in enumerate(result):
        if (item['input_lempos1'] != collocations[idx].lempos1 or item['input_lempos2'] != collocations[idx].lempos2 or
                item['input_type'] != collocations[idx].type):
            raise DatabaseInconsistency("values sent to database do not match the returned values " + "\n" +
                                        item['input_lempos1'] + " " + collocations[idx].lempos1 + "\n" +
                                        item['input_lempos2'] + " " + collocations[idx].lempos2 + "\n" +
                                        item['input_type'] + " " + collocations[idx].type)
        collocations[idx].metric = item['metric']


def _close_db():
    global _db
    if _db is not None:
        _db.close()


atexit.register(_close_db)
