#!/usr/bin/env python3
import argparse
import socket
import concurrent.futures
import datetime
import json
import csv
import subprocess
import sys
import os
import logging
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

logging.basicConfig(
    filename='port_scanner.log',
    filemode='a',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)

def banner():
    banner_text = """
╔════════════════════════════════════════════════════════╗
║                ⚡ ADVANCED PORT SCANNER                ║
║                   Coded by INTELEON404                 ║
╚════════════════════════════════════════════════════════╝
"""
    console.print(banner_text, style="cyan bold")

def is_host_online(target, timeout=1):
    try:
        param = '-c' if sys.platform != 'win32' else '-n'
        command = ['ping', param, '1', '-W', str(timeout), target] if sys.platform != 'win32' else ['ping', param, '1', '-w', str(timeout*1000), target]
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Ping error: {e}")
        return False

def traceroute(target):
    console.print(f"[~] Running traceroute on {target} ...\n", style="yellow")
    try:
        command = ['traceroute', target] if sys.platform != 'win32' else ['tracert', target]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            console.print(line.strip())
    except Exception as e:
        console.print(f"[!] Traceroute error: {e}", style="red")

def scan_port(target, port, timeout=2):
    service_name = "unknown"
    banner_info = "-"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((target, port))
            if result == 0:
                try:
                    service_name = socket.getservbyport(port)
                except:
                    service_name = "unknown"

                # Banner grabbing for HTTP/S ports
                if port in (80, 443, 8080, 8443):
                    try:
                        if port in (443, 8443):
                            import ssl
                            context = ssl.create_default_context()
                            with socket.create_connection((target, port), timeout=timeout) as sock:
                                with context.wrap_socket(sock, server_hostname=target) as ssock:
                                    ssock.settimeout(timeout)
                                    ssock.sendall(b"HEAD / HTTP/1.0\r\nHost: " + target.encode() + b"\r\n\r\n")
                                    resp = ssock.recv(1024).decode(errors='ignore')
                                    for line in resp.splitlines():
                                        if line.lower().startswith("server:"):
                                            banner_info = line.partition(":")[2].strip()
                                            break
                        else:
                            s.sendall(b"HEAD / HTTP/1.0\r\nHost: " + target.encode() + b"\r\n\r\n")
                            resp = s.recv(1024).decode(errors='ignore')
                            for line in resp.splitlines():
                                if line.lower().startswith("server:"):
                                    banner_info = line.partition(":")[2].strip()
                                    break
                    except Exception:
                        pass

                return (port, "Open", service_name, banner_info)
            else:
                return None
    except Exception as e:
        logging.debug(f"Port {port} scan error: {e}")
        return None

def parse_port_range(port_range_str):
    start, end = 1, 1024
    if port_range_str:
        if "-" in port_range_str:
            parts = port_range_str.split("-")
            if len(parts) == 2:
                try:
                    start = int(parts[0])
                    end = int(parts[1])
                except:
                    pass
        else:
            try:
                end = int(port_range_str)
            except:
                pass
    return start, end

def save_report_json(target, open_ports, scan_duration, filename):
    data = {
        "target": target,
        "scan_duration": str(scan_duration),
        "open_ports": [
            {
                "port": p[0],
                "status": p[1],
                "service": p[2],
                "version_info": p[3]
            } for p in open_ports
        ]
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    console.print(f"[+] JSON report saved to {filename}", style="green")

def save_report_csv(target, open_ports, scan_duration, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Port', 'Status', 'Service', 'Version Info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for port, status, service, version in open_ports:
            writer.writerow({'Port': port, 'Status': status, 'Service': service, 'Version Info': version})
    console.print(f"[+] CSV report saved to {filename}", style="green")

def print_scan_results(target, open_ports, scan_duration):
    table = Table(title=f"Scan Results for {target}", title_style="bold cyan")
    table.add_column("Port", justify="right", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="green")
    table.add_column("Service", justify="left", style="magenta")
    table.add_column("Version Info", justify="left", style="yellow")

    for port, status, service, version in sorted(open_ports):
        table.add_row(str(port), status, service, version)

    console.print(table)
    console.print(f"[+] Total open ports: {len(open_ports)}", style="bold green")
    console.print(f"[+] Scan duration: {scan_duration}", style="bold yellow")

def main():
    parser = argparse.ArgumentParser(
        description="Advanced Full Port Scanner with Basic Service Version Detection by INTELEON404",
        epilog="Example usage:\n  python3 scan.py -t 192.168.1.1 -r 1-65535 -th 500 -to 2 --traceroute",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-t", "--target", type=str, required=True,
                        help="Target IP(s) or domain(s) separated by commas")
    parser.add_argument("-r", "--range", type=str, default="1-1024",
                        help="Port range to scan. Format: start-end or single number (default: 1-1024)")
    parser.add_argument("-th", "--threads", type=int, default=500,
                        help="Max concurrent threads (default: 500)")
    parser.add_argument("-to", "--timeout", type=int, default=2,
                        help="Timeout seconds per port scan attempt (default: 2)")
    parser.add_argument("--traceroute", action="store_true",
                        help="Run traceroute after scanning")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose logging")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        console.print("[*] Verbose logging enabled", style="yellow")

    banner()

    targets = [t.strip() for t in args.target.split(",")]
    start_port, end_port = parse_port_range(args.range)

    # Removed printing starting scan targets line as requested
    # console.print(f"[~] Starting scan on targets: {targets}", style="cyan")
    console.print(f"[~] Port range: {start_port} to {end_port}", style="cyan")
    console.print(f"[~] Max Threads: {args.threads}", style="cyan")

    for target in targets:
        console.print(Panel.fit(f"Scanning Target: {target}", style="bold magenta"))

        console.print(f"[~] Pinging {target} to check if online...", style="yellow")
        online = is_host_online(target)
        if not online:
            console.print(f"[-] {target} appears to be offline or unreachable. Skipping...", style="red")
            continue
        else:
            console.print(f"[+] {target} is ONLINE\n", style="green")

        open_ports = []
        start_time = datetime.datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = {executor.submit(scan_port, target, port, args.timeout): port for port in range(start_port, end_port + 1)}

            with Progress(
                SpinnerColumn(),
                "[progress.description]{task.description}",
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.1f}%",
                TimeElapsedColumn(),
                transient=True,
                console=console
            ) as progress:

                task = progress.add_task(f"Scanning {target}", total=(end_port - start_port + 1))

                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    progress.advance(task)
                    if res and res not in open_ports:
                        open_ports.append(res)

        duration = datetime.datetime.now() - start_time

        print_scan_results(target, open_ports, duration)

        if Confirm.ask("[?] Save report to file?"):
            report_dir = "scan_reports"
            if not os.path.exists(report_dir):
                os.mkdir(report_dir)
            base_filename = f"{target.replace('.', '_')}_{start_port}-{end_port}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            json_filename = os.path.join(report_dir, base_filename + ".json")
            csv_filename = os.path.join(report_dir, base_filename + ".csv")

            fmt = Prompt.ask("Choose report format", choices=["json", "csv", "both"], default="both")
            if fmt in ("json", "both"):
                save_report_json(target, open_ports, duration, json_filename)
            if fmt in ("csv", "both"):
                save_report_csv(target, open_ports, duration, csv_filename)

        if args.traceroute:
            traceroute(target)

    console.print("[+] Scan finished.", style="bold green")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[!] Scan interrupted by user.", style="red")
        sys.exit(0)
