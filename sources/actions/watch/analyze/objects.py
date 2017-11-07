
from .auxiliary import analyze


def run(address=None, port=None, timeout=None, all=False, nogroup=False, sort=None, order=None, limit=None):
    """
    analyze server object changes
    :param address: specifies server address
    :param int port: specifies server port
    :param float timeout: specifies timeout to wait for reply
    :param switch all: disable objects filtering
    :param switch nogroup: disable grouping by name
    :param sort: sort entries by "name" or by "counter"
    :param order: sort entries "asc"ending or "desc"ending
    :param int limit: limit output
    """
    analyze("objects", address, port, timeout, all, nogroup, sort, order, limit)
