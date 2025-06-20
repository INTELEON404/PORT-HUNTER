# Advanced Port Scanner

⚡ **Advanced Port Scanner** is a powerful multi-threaded port scanning tool that scans specified IP addresses or domains over a range of ports. It detects open ports, basic service names, and performs simple version detection (e.g., HTTP server banners).

Created by: **INTELEON404**

---

## Features

- Multi-threaded scanning (default 500 threads) for fast performance
- Customizable port range scanning
- Host alive check using ping before scanning
- Basic banner grabbing for HTTP/HTTPS services
- Beautiful terminal output with [Rich](https://github.com/Textualize/rich) library
- Save scan reports as JSON or CSV files
- Optional traceroute after scan
- User-friendly CLI with detailed help and options

---

## Requirements

- Python 3.7+
- Python package: `rich`

Install dependencies via pip:

```bash
pip install rich
````

---

## Usage

Run the scanner using:

```bash
python3 scan.py -t 192.168.1.1,google.com -r 1-1024 -th 500 -to 2 --traceroute
```

### Command Line Options

| Option           | Description                                                    | Default      |
| ---------------- | -------------------------------------------------------------- | ------------ |
| `-t, --target`   | Target IP(s) or domain(s), separate multiple targets by commas | **Required** |
| `-r, --range`    | Port range to scan (e.g., 1-1024 or 80)                        | 1-1024       |
| `-th, --threads` | Maximum concurrent threads                                     | 500          |
| `-to, --timeout` | Timeout in seconds per port scan attempt                       | 2            |
| `--traceroute`   | Run traceroute after scanning                                  | False        |
| `-v, --verbose`  | Enable verbose debug logging                                   | False        |

---

## Example Output

```
╔════════════════════════════════════════════════════════╗
║                ⚡ ADVANCED PORT SCANNER                ║
║                   Coded by INTELEON404                 ║
╚════════════════════════════════════════════════════════╝

[~] Port range: 1 to 1024
[~] Max Threads: 500

╭──────────────────────────────╮
│ Scanning Target: 192.168.1.1 │
╰──────────────────────────────╯
[~] Pinging 192.168.1.1 to check if online...
[+] 192.168.1.1 is ONLINE

       Scan Results for 192.168.1.1       
┏━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Port ┃ Status ┃ Service ┃ Version Info ┃
┡━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩
│   80 │  Open  │ http    │ Apache/2.4.41 │
└──────┴────────┴─────────┴──────────────┘

[+] Total open ports: 1
[+] Scan duration: 0:00:06.021
[?] Save report to file? [y/n]:
```

---

## Future Improvements

* Advanced service version fingerprinting
* Banner grabbing for additional protocols (FTP, SSH, SMTP, etc.)
* Web-based interface for scanning and reporting
* Built-in exploit detection

---

## License

MIT License © 2025 INTELEON404

---

## Contact

* Email: [inteleon404@gmail.com](mailto:inteleon404@gmail.com)
* GitHub: [https://github.com/INTELEON404](https://github.com/INTELEON404)

---

**Feedback and contributions are welcome. Thank you!**



---

If you want, I can also help create installation instructions, examples, or contribution guidelines. Let me know!

