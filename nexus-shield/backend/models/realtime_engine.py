"""
Real-Time Network Monitor
Uses psutil to capture ACTUAL live network stats from the machine.
No root/admin needed — works on Windows, Mac, Linux.
"""
import psutil
import time
import socket
import collections
from typing import Dict, List

# ── Rolling window for rate calculations ─────────────────────────────────────
_prev_net   = None
_prev_time  = None
_rate_history: List[float] = []
_conn_history: collections.deque = collections.deque(maxlen=60)

# Track suspicious connection patterns
_port_access_counter: collections.Counter = collections.Counter()
_ip_access_counter:   collections.Counter = collections.Counter()
_last_connections:    List[Dict] = []


def get_real_network_stats() -> Dict:
    """
    Returns real live network metrics from this machine:
    - bytes_sent/recv per second
    - packets_sent/recv per second  
    - active TCP connections
    - suspicious port/IP patterns
    """
    global _prev_net, _prev_time, _rate_history

    now     = time.time()
    net_io  = psutil.net_io_counters()

    if _prev_net is None:
        _prev_net  = net_io
        _prev_time = now
        return _build_empty_stats()

    elapsed = now - _prev_time
    if elapsed < 0.1:
        return _build_empty_stats()

    # ── Rates ─────────────────────────────────────────────────────────────────
    bytes_sent_rate  = (net_io.bytes_sent  - _prev_net.bytes_sent)  / elapsed
    bytes_recv_rate  = (net_io.bytes_recv  - _prev_net.bytes_recv)  / elapsed
    pkts_sent_rate   = (net_io.packets_sent - _prev_net.packets_sent) / elapsed
    pkts_recv_rate   = (net_io.packets_recv - _prev_net.packets_recv) / elapsed
    total_pkt_rate   = pkts_sent_rate + pkts_recv_rate

    _prev_net  = net_io
    _prev_time = now

    _rate_history.append(total_pkt_rate)
    if len(_rate_history) > 60:
        _rate_history.pop(0)

    # ── Live TCP connections ───────────────────────────────────────────────────
    connections   = []
    suspicious    = []
    try:
        conns = psutil.net_connections(kind="inet")
        for c in conns:
            if c.status == "ESTABLISHED" and c.raddr:
                entry = {
                    "local_port":  c.laddr.port if c.laddr else 0,
                    "remote_ip":   c.raddr.ip   if c.raddr else "",
                    "remote_port": c.raddr.port if c.raddr else 0,
                    "status":      c.status,
                    "pid":         c.pid,
                }
                connections.append(entry)
                _port_access_counter[c.laddr.port if c.laddr else 0] += 1
                _ip_access_counter[c.raddr.ip if c.raddr else ""] += 1

        # Flag suspicious: same IP hitting many ports (port scan pattern)
        for ip, count in _ip_access_counter.most_common(5):
            if count > 10 and ip not in ("127.0.0.1", "::1", ""):
                suspicious.append({
                    "type": "PORT_SCAN_PATTERN",
                    "ip": ip,
                    "connections": count,
                })

        # Flag: too many connections from same IP (DoS pattern)
        for ip, count in _ip_access_counter.most_common(3):
            if count > 50:
                suspicious.append({
                    "type": "DOS_PATTERN",
                    "ip": ip,
                    "connections": count,
                })

    except (psutil.AccessDenied, Exception):
        pass

    # ── CPU / Memory (system health) ──────────────────────────────────────────
    cpu_pct = psutil.cpu_percent(interval=None)
    mem     = psutil.virtual_memory()

    # ── Threat heuristic from real traffic ────────────────────────────────────
    real_threat = _calculate_real_threat(total_pkt_rate, len(connections), len(suspicious))

    return {
        "packet_rate":       round(total_pkt_rate, 1),
        "bytes_sent_rate":   round(bytes_sent_rate / 1024, 1),   # KB/s
        "bytes_recv_rate":   round(bytes_recv_rate / 1024, 1),   # KB/s
        "pkts_sent_rate":    round(pkts_sent_rate, 1),
        "pkts_recv_rate":    round(pkts_recv_rate, 1),
        "active_connections": len(connections),
        "suspicious_patterns": suspicious,
        "top_connections":   connections[:5],
        "cpu_percent":       cpu_pct,
        "memory_percent":    round(mem.percent, 1),
        "real_threat_level": real_threat,
        "rate_history":      _rate_history[-30:],
        "total_bytes_sent":  net_io.bytes_sent,
        "total_bytes_recv":  net_io.bytes_recv,
        "total_pkts_sent":   net_io.packets_sent,
        "total_pkts_recv":   net_io.packets_recv,
        "errin":             net_io.errin,
        "errout":            net_io.errout,
        "dropin":            net_io.dropin,
        "dropout":           net_io.dropout,
    }


def _calculate_real_threat(pkt_rate: float, conn_count: int, suspicious_count: int) -> float:
    """Heuristic threat score from real traffic (0.0 - 1.0)."""
    score = 0.0

    # High packet rate
    if pkt_rate > 5000:   score += 0.6
    elif pkt_rate > 1000: score += 0.3
    elif pkt_rate > 500:  score += 0.1

    # Many connections
    if conn_count > 200:  score += 0.3
    elif conn_count > 100: score += 0.15
    elif conn_count > 50:  score += 0.05

    # Suspicious patterns detected
    score += suspicious_count * 0.2

    return round(min(1.0, score), 3)


def _build_empty_stats() -> Dict:
    return {
        "packet_rate": 0, "bytes_sent_rate": 0, "bytes_recv_rate": 0,
        "pkts_sent_rate": 0, "pkts_recv_rate": 0,
        "active_connections": 0, "suspicious_patterns": [],
        "top_connections": [], "cpu_percent": 0, "memory_percent": 0,
        "real_threat_level": 0.0, "rate_history": [],
        "total_bytes_sent": 0, "total_bytes_recv": 0,
        "total_pkts_sent": 0, "total_pkts_recv": 0,
        "errin": 0, "errout": 0, "dropin": 0, "dropout": 0,
    }


def get_network_interfaces() -> List[Dict]:
    """Get all active network interfaces with their stats."""
    interfaces = []
    try:
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        io    = psutil.net_io_counters(pernic=True)

        for name, stat in stats.items():
            if not stat.isup:
                continue
            ips = [a.address for a in addrs.get(name, [])
                   if a.family == socket.AF_INET]
            nic_io = io.get(name)
            interfaces.append({
                "name":    name,
                "speed":   stat.speed,
                "mtu":     stat.mtu,
                "ips":     ips,
                "bytes_sent": nic_io.bytes_sent if nic_io else 0,
                "bytes_recv": nic_io.bytes_recv if nic_io else 0,
            })
    except Exception:
        pass
    return interfaces
