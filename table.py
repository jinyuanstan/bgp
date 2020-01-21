# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, SmallInteger, String, Text, text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Locker(Base):
    __tablename__ = '_locker'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, server_default=text("''"))
    clientset_id = Column(Integer)
    domain_pool_id = Column(Integer)
    netlink_id = Column(Integer)
    viewer_id = Column(Integer)
    routeset_id = Column(Integer)
    domainlink_id = Column(Integer)
    netlinkset_id = Column(Integer)
    route_id = Column(Integer)
    outlink_id = Column(Integer)
    policy_id = Column(Integer)
    policy_detail_id = Column(Integer)
    ldns_id = Column(Integer)


class Clientset(Base):
    __tablename__ = 'clientset'

    id = Column(Integer, primary_key=True)
    name = Column(String(127), nullable=False)
    info = Column(String(255), nullable=False, server_default=text("''"))


class Cp(Base):
    __tablename__ = 'cp'

    id = Column(Integer, primary_key=True)
    neighbor = Column(String(64), nullable=False,unique=True)
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    lastup = Column(DateTime)
    lastdown = Column(DateTime)
    prefixes = Column(Integer, nullable=False, server_default=text("'0'"))
    updown = Column(Integer, nullable=False, server_default=text("'0'"))


class Cproute(Base):
    __tablename__ = 'cproute'

    id = Column(Integer, primary_key=True)
    neighbor = Column(String(64), nullable=False)
    prefix = Column(String(64), nullable=False)
    length = Column(Integer, nullable=False)
    ip_start = Column(Numeric(39, 0), nullable=False)
    ip_end = Column(Numeric(39, 0), nullable=False)
    aspath = Column(String(512), nullable=False)
    nexthop = Column(String(64), nullable=False)
    community = Column(Text, nullable=False)
    extended_community = Column(Text, nullable=False)
    origin = Column(String(10), nullable=False)
    originas = Column(Integer, nullable=False)
    time = Column(DateTime, nullable=False, server_default=text("'0000-00-00 00:00:00'"))


class DnsForwardZone(Base):
    __tablename__ = 'dns_forward_zone'

    id = Column(Integer, primary_key=True)
    dm = Column(String(255))
    typ = Column(String(16), nullable=False, server_default=text("'only'"))


class DnsForwarder(Base):
    __tablename__ = 'dns_forwarders'

    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer)
    ldns_id = Column(Integer)


class Domain(Base):
    __tablename__ = 'domain'

    id = Column(Integer, primary_key=True)
    domain = Column(String(255), nullable=False)
    domain_pool_id = Column(Integer)


class DomainPool(Base):
    __tablename__ = 'domain_pool'

    id = Column(Integer, primary_key=True)
    name = Column(String(127), nullable=False)
    info = Column(String(255), nullable=False, server_default=text("''"))
    typ = Column(String(16), nullable=False, server_default=text("'normal'"))
    enable = Column(Integer, nullable=False, server_default=text("'1'"))
    unavailable = Column(SmallInteger, nullable=False, server_default=text("'0'"))
    domain_monitor = Column(Integer, nullable=False, server_default=text("'0'"))


class Domainlink(Base):
    __tablename__ = 'domainlink'

    id = Column(Integer, primary_key=True)
    domain_pool_id = Column(Integer, nullable=False)
    netlink_id = Column(Integer, nullable=False)
    netlinkset_id = Column(Integer, nullable=False)
    enable = Column(Integer, nullable=False, server_default=text("'1'"))


class Filter(Base):
    __tablename__ = 'filter'

    id = Column(Integer, primary_key=True)
    src_ip_start = Column(String(40))
    src_ip_end = Column(String(40))
    clientset_id = Column(Integer)
    domain_id = Column(Integer)
    domain_pool_id = Column(Integer)
    dst_ip_start = Column(String(40))
    dst_ip_end = Column(String(40))
    netlink_id = Column(Integer)
    target_ip = Column(String(40))
    outlink_id = Column(Integer)
    enable = Column(Integer, nullable=False, server_default=text("'1'"))


class Ipnet(Base):
    __tablename__ = 'ipnet'

    id = Column(Integer, primary_key=True)
    ip_start = Column(String(40), nullable=False)
    ip_end = Column(String(40), nullable=False)
    ipnet = Column(String(40), nullable=False)
    mask = Column(Integer, nullable=False)
    clientset_id = Column(Integer)


class IpnetWl(Base):
    __tablename__ = 'ipnet_wl'

    id = Column(Integer, primary_key=True)
    ip_start = Column(String(40), nullable=False)
    ip_end = Column(String(40), nullable=False)
    ipnet = Column(String(40), nullable=False)
    mask = Column(Integer, nullable=False)
    clientset_id = Column(Integer)


class Iptable(Base):
    __tablename__ = 'iptable'

    id = Column(Integer, primary_key=True)
    ip_start = Column(String(40), nullable=False)
    ip_end = Column(String(40), nullable=False)
    ipnet = Column(String(40), nullable=False)
    mask = Column(Integer, nullable=False)
    netlink_id = Column(Integer)


class IptableWl(Base):
    __tablename__ = 'iptable_wl'

    id = Column(Integer, primary_key=True)
    ip_start = Column(String(40), nullable=False)
    ip_end = Column(String(40), nullable=False)
    ipnet = Column(String(40), nullable=False)
    mask = Column(Integer, nullable=False)
    netlink_id = Column(Integer)


class Ldn(Base):
    __tablename__ = 'ldns'

    id = Column(Integer, primary_key=True)
    name = Column(String(127), nullable=False)
    addr = Column(String(40), nullable=False)
    typ = Column(String(32), nullable=False, server_default=text("'upstream'"))
    checkdm = Column(String(64), nullable=False, server_default=text("'baidu.com'"))
    enable = Column(Integer, nullable=False, server_default=text("'1'"))
    unavailable = Column(SmallInteger, nullable=False, server_default=text("'0'"))


class Natlink(Base):
    __tablename__ = 'natlink'

    id = Column(Integer, primary_key=True)
    outlink_id = Column(Integer)
    natserver_id = Column(Integer)
    status = Column(Integer, nullable=False, server_default=text("'1'"))
    gw = Column(String(126), nullable=False)
    addr = Column(String(255), nullable=False)


class Natserver(Base):
    __tablename__ = 'natserver'

    id = Column(Integer, primary_key=True)
    name = Column(String(127), nullable=False)
    addr = Column(String(127), nullable=False)
    enable = Column(Integer, nullable=False, server_default=text("'1'"))
    unavailable = Column(SmallInteger, nullable=False, server_default=text("'0'"))


class Netlink(Base):
    __tablename__ = 'netlink'

    id = Column(Integer, primary_key=True)
    isp = Column(String(127), nullable=False)
    region = Column(String(127), nullable=False, server_default=text("''"))
    typ = Column(String(32), nullable=False, server_default=text("'normal'"))


class Netlinkset(Base):
    __tablename__ = 'netlinkset'

    id = Column(Integer, primary_key=True)
    name = Column(String(127), nullable=False)


class Oplog(Base):
    __tablename__ = 'oplog'

    id = Column(BigInteger, primary_key=True)
    opr = Column(String(16))
    action = Column(String(6))
    tbl = Column(String(16))
    row_id = Column(Integer)
    time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class Outlink(Base):
    __tablename__ = 'outlink'

    id = Column(Integer, primary_key=True)
    name = Column(String(127), nullable=False)
    addr = Column(String(255), nullable=False)
    typ = Column(String(32), nullable=False, server_default=text("'normal'"))
    enable = Column(Integer, nullable=False, server_default=text("'1'"))
    unavailable = Column(SmallInteger, nullable=False, server_default=text("'0'"))


class Policy(Base):
    __tablename__ = 'policy'

    id = Column(Integer, primary_key=True)
    name = Column(String(127), nullable=False)


class PolicyDetail(Base):
    __tablename__ = 'policy_detail'

    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, nullable=False)
    policy_sequence = Column(Integer, nullable=False, server_default=text("'0'"))
    enable = Column(Integer, nullable=False, server_default=text("'1'"))
    priority = Column(SmallInteger, nullable=False, server_default=text("'20'"))
    weight = Column(SmallInteger, nullable=False, server_default=text("'100'"))
    op = Column(String(127), nullable=False, server_default=text("'and'"))
    op_typ = Column(String(32), nullable=False, server_default=text("'builtin'"))
    ldns_id = Column(Integer, nullable=False)
    rrset_id = Column(Integer)


class Route(Base):
    __tablename__ = 'route'

    id = Column(Integer, primary_key=True)
    routeset_id = Column(Integer, nullable=False)
    netlinkset_id = Column(Integer, nullable=False)
    outlink_id = Column(Integer, nullable=False)
    enable = Column(Integer, nullable=False, server_default=text("'1'"))
    priority = Column(SmallInteger, nullable=False, server_default=text("'20'"))
    score = Column(SmallInteger, nullable=False, server_default=text("'50'"))
    unavailable = Column(SmallInteger, nullable=False, server_default=text("'0'"))


class Routeset(Base):
    __tablename__ = 'routeset'

    id = Column(Integer, primary_key=True)
    name = Column(String(127), nullable=False)
    info = Column(String(255), nullable=False, server_default=text("''"))


class Rr(Base):
    __tablename__ = 'rr'

    id = Column(Integer, primary_key=True)
    rrtype = Column(Integer, nullable=False)
    rrdata = Column(String(255), nullable=False)
    ttl = Column(Integer, nullable=False, server_default=text("'300'"))
    rrset_id = Column(Integer)
    enable = Column(Integer, nullable=False, server_default=text("'1'"))


class Rrset(Base):
    __tablename__ = 'rrset'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, server_default=text("''"))
    enable = Column(Integer, nullable=False, server_default=text("'1'"))


class Viewer(Base):
    __tablename__ = 'viewer'

    id = Column(Integer, primary_key=True)
    clientset_id = Column(Integer, nullable=False)
    domain_pool_id = Column(Integer, nullable=False)
    routeset_id = Column(Integer, nullable=False)
    policy_id = Column(Integer, nullable=False)
    enable = Column(Integer, nullable=False, server_default=text("'1'"))
