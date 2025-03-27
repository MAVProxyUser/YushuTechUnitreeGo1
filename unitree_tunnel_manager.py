import requests
import json
from typing import Dict, List, Tuple
import urllib3
import sqlite3
import os
import sys
import time
from datetime import datetime, timedelta
import threading
import queue
import termios
import tty
import readline
import atexit
import select
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from ipwhois import IPWhois
from time import sleep
from contextlib import contextmanager
from queue import Queue, Empty
from pprint import pprint


# Disable SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class KeyboardListener:
    def __init__(self):
        self.should_stop = False

    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, *args):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def check_key(self):
        if sys.stdin.read(1) == 'q':
            self.should_stop = True

class RateLimiter:
    def __init__(self, requests_per_minute=15):
        self.requests_per_minute = requests_per_minute
        self.requests = []
        
    def wait_if_needed(self):
        """Wait if we're over the rate limit"""
        now = datetime.now()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(minutes=1)]
        
        if len(self.requests) >= self.requests_per_minute:
            # Calculate sleep time
            oldest_request = min(self.requests)
            sleep_time = 60 - (now - oldest_request).seconds
            if sleep_time > 0:
                print(f"\nRate limit reached, waiting {sleep_time} seconds...")
                time.sleep(sleep_time)
        
        self.requests.append(now)

class DatabaseConnectionPool:
    """Thread-safe SQLite connection pool implementation"""
    def __init__(self, database, max_connections=5):
        self.database = database
        self.max_connections = max_connections
        self.connections = Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self.local = threading.local()
        self._fill_pool()

    def _fill_pool(self):
        """Initialize the connection pool"""
        for _ in range(self.max_connections):
            self.connections.put(None)  # Reserve slots but don't create connections yet

    def _create_connection(self):
        """Create a new database connection for the current thread"""
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def get_connection(self):
        """Get a thread-local connection with context management"""
        # Check if we already have a connection for this thread
        if not hasattr(self.local, 'connection'):
            # Get a slot from the pool
            try:
                self.connections.get(timeout=5)  # Just get a slot
                self.local.connection = self._create_connection()
            except Empty:
                raise RuntimeError("Could not get a database connection from the pool")

        try:
            yield self.local.connection
            self.local.connection.commit()  # Commit any pending transactions
        except Exception as e:
            self.local.connection.rollback()  # Rollback on error
            raise e

    def close_all(self):
        """Close all connections in the pool"""
        with self.lock:
            # Close the thread-local connection if it exists
            if hasattr(self.local, 'connection'):
                self.local.connection.close()
                delattr(self.local, 'connection')
            
            # Clear the pool
            while not self.connections.empty():
                try:
                    self.connections.get_nowait()
                except Empty:
                    break

class Database:
    def __init__(self, db_path="tunnels.db"):
        self.db_path = db_path
        self.pool = DatabaseConnectionPool(db_path)
        self.init_db()

    def init_db(self):
        """Initialize database schema"""
        with self.pool.get_connection() as conn:
            # Add enhanced lookup fields
            try:
                # Fields matching IP-API response
                conn.execute("ALTER TABLE machines ADD COLUMN dns_hostname TEXT")
                conn.execute("ALTER TABLE machines ADD COLUMN dns_status TEXT")
                conn.execute("ALTER TABLE machines ADD COLUMN dns_country TEXT")
                conn.execute("ALTER TABLE machines ADD COLUMN dns_city TEXT")
                conn.execute("ALTER TABLE machines ADD COLUMN dns_org TEXT")
                conn.execute("ALTER TABLE machines ADD COLUMN dns_isp TEXT")
                conn.execute("ALTER TABLE machines ADD COLUMN dns_asn TEXT")
                conn.execute("ALTER TABLE machines ADD COLUMN dns_is_mobile INTEGER")
                conn.execute("ALTER TABLE machines ADD COLUMN dns_is_proxy INTEGER")
                conn.execute("ALTER TABLE machines ADD COLUMN dns_is_hosting INTEGER")
                conn.execute("ALTER TABLE machines ADD COLUMN dns_last_lookup TEXT")
            except sqlite3.OperationalError:
                # Columns might already exist
                pass

            conn.execute("""
                CREATE TABLE IF NOT EXISTS machines (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    os TEXT,
                    ip TEXT,
                    public_ip TEXT,
                    mac TEXT,
                    version TEXT,
                    is_active INTEGER,
                    active_time TEXT,
                    add_time TEXT,
                    last_updated TEXT,
                    dns_hostname TEXT,
                    dns_status TEXT,
                    dns_country TEXT,
                    dns_city TEXT,
                    dns_org TEXT,
                    dns_isp TEXT,
                    dns_asn TEXT,
                    dns_is_mobile INTEGER,
                    dns_is_proxy INTEGER,
                    dns_is_hosting INTEGER,
                    dns_last_lookup TEXT
                )
            """)

    def update_machines(self, machines: List[Dict]):
        current_time = datetime.now().isoformat()
        with self.pool.get_connection() as conn:
            for machine in machines:
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO machines 
                        (id, name, os, ip, public_ip, mac, version, is_active, 
                         active_time, add_time, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        machine['id'],
                        machine['name'],
                        machine.get('os', ''),
                        machine.get('ip', ''),
                        machine.get('publicIP', ''),
                        machine.get('mac', ''),
                        machine.get('version', ''),
                        machine.get('isActive', 0),
                        machine.get('activetime', ''),
                        machine.get('addtime', ''),
                        current_time
                    ))
                except sqlite3.Error as e:
                    print(f"\nError updating machine {machine.get('id', 'unknown')}: {str(e)}")
                    continue

    def get_machines_for_display(self, page: int, page_size: int, filters: Dict = None) -> Tuple[List[Dict], int]:
        """Get paginated and filtered machines"""
        query = "SELECT * FROM machines"
        params = []
        
        if filters:
            conditions = []
            if 'm' in filters:
                conditions.append("name LIKE ?")
                params.append(f"%{filters['m']}%")
            if 'i' in filters:
                conditions.append("(ip LIKE ? OR public_ip LIKE ?)")
                params.extend([f"%{filters['i']}%", f"%{filters['i']}%"])
            if 's' in filters:
                state_map = {'active': 1, 'inactive': 0}
                if filters['s'].lower() in state_map:
                    conditions.append("is_active = ?")
                    params.append(state_map[filters['s'].lower()])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM ({query})"
        
        with self.pool.get_connection() as conn:
            total = conn.execute(count_query, params).fetchone()['count']
            
            # Add pagination
            query += " ORDER BY active_time DESC NULLS LAST LIMIT ? OFFSET ?"
            params.extend([page_size, page * page_size])
            
            results = conn.execute(query, params).fetchall()
            return [dict(row) for row in results], total

    def analyze_organizations(self):
        """Analyze organizations via enhanced IP lookups"""
        print("\nAnalyzing organizations via IP lookups...")
        
        # Get IPs needing lookup
        with self.pool.get_connection() as conn:
            new_ips = conn.execute("""
                SELECT DISTINCT public_ip 
                FROM machines 
                WHERE public_ip != '' 
                AND public_ip IS NOT NULL
                AND dns_last_lookup IS NULL
            """).fetchall()
            new_ips = {row['public_ip'] for row in new_ips}

        if not new_ips:
            print("No new IPs to analyze.")
            return

        print(f"Processing {len(new_ips)} IP addresses...")
        results = self.batch_reverse_dns_lookup(list(new_ips))
        current_time = datetime.now().isoformat()
        
        # Update DNS information
        with self.pool.get_connection() as conn:
            for result in results:
                conn.execute("""
                    UPDATE machines 
                    SET dns_hostname = ?,
                        dns_status = ?,
                        dns_country = ?,
                        dns_city = ?,
                        dns_org = ?,
                        dns_isp = ?,
                        dns_asn = ?,
                        dns_is_mobile = ?,
                        dns_is_proxy = ?,
                        dns_is_hosting = ?,
                        dns_last_lookup = ?
                    WHERE public_ip = ?
                """, (
                    result['hostname'],
                    result['status'],
                    result['country'],
                    result['city'],
                    result['org'],
                    result['isp'],
                    result['asn'],
                    result['is_mobile'],
                    result['is_proxy'],
                    result['is_hosting'],
                    current_time,
                    result['ip']
                ))

    def __del__(self):
        """Cleanup connection pool on deletion"""
        self.pool.close_all()

    def get_whois_org_info(self, ip: str) -> Dict:
        """Get organization information using ipwhois as fallback"""
        try:
            obj = IPWhois(ip)
            result = obj.lookup_rdap(depth=1)
            return {
                'org': result.get('network', {}).get('name'),
                'asn': f"AS{result.get('asn')}",
                'asn_description': result.get('asn_description')
            }
        except Exception:
            return {'org': None, 'asn': None, 'asn_description': None}

    def batch_reverse_dns_lookup(self, ips: List[str]) -> List[Dict]:
        """Perform batch IP lookup using WHOIS first, then ip-api.com as fallback"""
        if not ips:
            return []

        batch_size = 100
        results = []
        rate_limiter = RateLimiter(requests_per_minute=15)
        total_batches = (len(ips) + batch_size - 1) // batch_size
        
        for batch_num, i in enumerate(range(0, len(ips), batch_size)):
            batch = list(ips)[i:i + batch_size]
            rate_limiter.wait_if_needed()
            
            batch_results = []
            for ip in batch:
                # Try WHOIS first
                whois_info = self.get_whois_org_info(ip)
                result = {
                    'status': 'success',
                    'country': None,
                    'city': None,
                    'org': whois_info['org'],
                    'isp': None,
                    'as': whois_info['asn'],
                    'mobile': False,
                    'proxy': False,
                    'hosting': False
                }
                
                # If WHOIS didn't provide org info, try ip-api
                if not whois_info['org']:
                    try:
                        fields = ["status", "country", "city", "org", "isp", "as", 
                                "mobile", "proxy", "hosting"]
                        
                        response = requests.post(
                            'http://ip-api.com/batch',
                            json=[{"query": ip, "fields": fields}],
                            timeout=10
                        )
                        
                        if response.status_code == 429:
                            print("\nRate limit exceeded, waiting for reset...")
                            time.sleep(60)
                            continue
                        
                        api_result = response.json()[0]
                        
                        # Update missing fields from ip-api
                        result.update({
                            'status': api_result.get('status'),
                            'country': api_result.get('country'),
                            'city': api_result.get('city'),
                            'org': api_result.get('org') or result['org'],
                            'isp': api_result.get('isp'),
                            'as': api_result.get('as') or result['as'],
                            'mobile': api_result.get('mobile', False),
                            'proxy': api_result.get('proxy', False),
                            'hosting': api_result.get('hosting', False)
                        })
                        
                    except Exception as e:
                        print(f"\nIP-API lookup failed for {ip}: {str(e)}")
                
                batch_results.append(result)
                
            # Store results for this batch
            for ip, result in zip(batch, batch_results):
                results.append({
                    'ip': ip,
                    'hostname': socket.getfqdn(ip),
                    'status': result.get('status'),
                    'country': result.get('country'),
                    'city': result.get('city'),
                    'org': result.get('org'),
                    'isp': result.get('isp'),
                    'asn': result.get('as'),
                    'is_mobile': 1 if result.get('mobile') else 0,
                    'is_proxy': 1 if result.get('proxy') else 0,
                    'is_hosting': 1 if result.get('hosting') else 0
                })
            
            progress = int((batch_num + 1) / total_batches * 50)
            percentage = int((batch_num + 1) / total_batches * 100)
            print(f"\rProgress: [{'=' * progress}{' ' * (50-progress)}] "
                  f"{percentage}% "
                  f"({(batch_num + 1) * batch_size}/{len(ips)})", end='', flush=True)
        
        print()  # New line after progress bar
        return results

class ZhexiAPI:
    def __init__(self, api_key: str, base_url: str = "https://yz.zhexi.tech"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        self.db = Database()
        self.update_queue = queue.Queue()
        self.is_updating = False

    def _make_request(self, endpoint: str, params: Dict = None, method: str = "GET") -> Dict:
        if params is None:
            params = {}
        
        url = f"{self.base_url}/api/v2/{endpoint}?apikey={self.api_key}"
        
        if method == "GET":
            response = self.session.get(url, params=params)
        elif method == "POST":
            response = self.session.post(url, json=params)
        ret = response.json()

        # pprint(ret)

        return ret

    def start_background_update(self):
        if not self.is_updating:
            self.is_updating = True
            thread = threading.Thread(target=self._background_update)
            thread.daemon = True
            thread.start()

    def start_online_machines_update(self):
        """Start background thread to only update online machines"""
        if not self.is_updating:
            self.is_updating = True
            thread = threading.Thread(target=self._update_online_machines)
            thread.daemon = True
            thread.start()

    def _background_update(self):
        page_size = 10
        from_page = 0

        # First request to get total count
        response = self._make_request("machine/list", params={"size": page_size, "from": from_page})
        total = response.get('total', 0)
        machines_processed = 0

        while machines_processed < total:
            response = self._make_request("machine/list", params={"size": page_size, "from": from_page})
            machines = response.get('data', [])
            
            if not machines:
                break

            self.db.update_machines(machines)
            machines_processed += len(machines)
            from_page += 1
            
            # Calculate progress percentage
            progress = int((machines_processed / total) * 50)
            percentage = int((machines_processed / total) * 100)
            
            # Create progress bar
            progress_bar = f"\rUpdating machines: [{'=' * progress}{' ' * (50-progress)}] {percentage}% ({machines_processed}/{total})"
            self.update_queue.put(progress_bar)

        # Verify final count
        with sqlite3.connect(self.db.db_path) as conn:
            final_count = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
        self.update_queue.put(f"\rUpdate complete! Total machines in database: {final_count}      \n")
        
        self.is_updating = False

    def _update_online_machines(self):
        """
        Update only machines that are currently online.
        This is more efficient than updating all machines.
        
        Process:
        1. Fetch only online machines from the API
        2. If successful, mark all machines as offline in the database
        3. Update online machines in the database
        """
        page_size = 10
        from_page = 0
        current_time = datetime.now().isoformat()
        
        # Step 1: First check if we can access the API and get online machines
        self.update_queue.put("\rFetching online machines from API...\n")
        
        # Initial API request to get total count of online machines
        try:
            response = self._make_request("machine/list", params={"size": page_size, "from": from_page, "online": 1})
            total = response.get('total', 0)
            
            if 'error' in response and response.get('error') != 0:
                self.update_queue.put(f"\rAPI Error: {response.get('info', 'Unknown error')}\n")
                self.is_updating = False
                return
            
            self.update_queue.put(f"\rFound {total} online machines. Preparing to update...\n")
            
            # If we got here, the API is responsive, so we can safely collect all online machines
            online_machines = []
            machines_processed = 0
            from_page = 0
            
            while machines_processed < total:
                response = self._make_request("machine/list", params={"size": page_size, "from": from_page, "online": 1})
                machines = response.get('data', [])
                
                if not machines:
                    break
                
                online_machines.extend(machines)
                machines_processed += len(machines)
                from_page += 1
                
                # Calculate progress percentage for fetching
                progress = int((machines_processed / total) * 50) if total > 0 else 50
                percentage = int((machines_processed / total) * 100) if total > 0 else 100
                
                # Create progress bar
                progress_bar = f"\rFetching online machines: [{'=' * progress}{' ' * (50-progress)}] {percentage}% ({machines_processed}/{total})"
                self.update_queue.put(progress_bar)
            
            # Step 2: Now that we have all online machines, mark all machines offline first
            with self.db.pool.get_connection() as conn:
                conn.execute("UPDATE machines SET is_active = 0, last_updated = ?", (current_time,))
                self.update_queue.put("\rMarked all machines as offline. Now updating online machines...\n")
            
            # Step 3: Update the online machines in the database
            if online_machines:
                self.db.update_machines(online_machines)
                
                # Verify final count of online machines
                with sqlite3.connect(self.db.db_path) as conn:
                    online_count = conn.execute("SELECT COUNT(*) FROM machines WHERE is_active = 1").fetchone()[0]
                    total_count = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
                
                self.update_queue.put(f"\rUpdate complete! Online machines: {online_count}/{total_count}      \n")
            else:
                self.update_queue.put(f"\rNo online machines found. All machines marked as offline.\n")
            
        except Exception as e:
            self.update_queue.put(f"\rError during update: {str(e)}\n")
        
        self.is_updating = False

    def list_valid_templates(self, tunnel_type: int, template_type: int = None, bandwidth: int = None) -> Dict:
        """
        Get list of valid tunnel templates
        
        Args:
            tunnel_type (int): Required. Tunnel type (0: TCP, 1: HTTP, 2: HTTPS, 5: UDP)
            template_type (int, optional): Template type
                0: Random port (custom)
                3: Same port (custom)
                254: 5 Yuan permanent free tunnel
                255: Free tunnel
            bandwidth (int, optional): Template bandwidth (1,2,4,8,12,16,20,24 Mbps)
        """
        params = {
            "tunnelType": tunnel_type,
            "size": 10  # Maximum allowed by API
        }
        
        if template_type is not None:
            params["type"] = template_type

        if bandwidth is not None:
            params["bandwidth"] = bandwidth
            
        return self._make_request("mapping/valid", params)

    def create_tunnel(self, machine_id: str, template_id: str = None, port: int = None) -> Dict:
        """Create an SSH tunnel for a specific machine
        
        Args:
            machine_id: ID of the target machine
            template_id: Optional. If provided, use this template. 
                        If None, create a new template.
        """
        
        # Step 1: If no template_id provided, create a new tunnel template
        if not template_id:
            expiry_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            template_params = {
                "amount": 1,
                "bandwidth": 4,
                "concurrency": 50,
                "expired_at": expiry_date
            }
            
            template_response = self._make_request("order/tunnel", params=template_params)
            
            if template_response.get('error', 1) != 0:
                return template_response
            
            template_id = template_response.get('data', {}).get('id')
            if not template_id:
                return {"error": 1, "info": "Failed to create tunnel template"}
            
            print(f"Created new tunnel template: {template_id}")
        
        # Step 2: Create the actual tunnel mapping
        params = {
            "machineID": machine_id,
            "templet": template_id,
            "type": 0,  # TCP
            "name": f"d_{machine_id}",
            "ip": "127.0.0.1",
            "port": port,
        }
        
        return self._make_request("mapping/tunnel", params=params, method="POST")

class InteractiveShell:
    def __init__(self, api):
        self.api = api
        self.page_size = 20
        self.current_page = 0
        self.keyboard_listener = None
        self.commands = {
            'p': self.print_tunnels,
            'print': self.print_tunnels,
            'n': self.next_page,
            'next': self.next_page,
            'prev': self.prev_page,
            'b': self.prev_page,
            'back': self.prev_page,
            'u': self.update_data,
            'update': self.update_data,
            'help': self.show_help,
            'h': self.show_help,
            'exit': self.exit,
            'e': self.exit,
            'quit': self.exit,
            'q': self.exit,
            't': self.list_templates,
            'templates': self.list_templates,
            'ssh': self.create_ssh_access,
            'connect': self.create_tunnel_to_port,
            'analyze': self.analyze_organizations,
            'dns': self.analyze_organizations,
            'export': self.export_to_csv,
            'csv': self.export_to_csv,
            'online': self.update_online_machines,
            'o': self.update_online_machines,
        }
        self.running = True
        self.current_filters = {}
        
        # Setup command history
        self.histfile = os.path.join(os.path.expanduser("~"), ".tunnel_history")
        try:
            readline.read_history_file(self.histfile)
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass
        
        # Register the history file to be saved on exit
        atexit.register(readline.write_history_file, self.histfile)
        
        # Set up tab completion
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.complete)

    def complete(self, text, state):
        """Tab completion function"""
        options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None

    def show_help(self, *args):
        print("\nAvailable commands:")
        print("  p, print [filter]  - Print machine list (optional filters)")
        print("    Filters:")
        print("      -m <machine_name>  - Filter by machine name")
        print("      -i <ip>           - Filter by IP or Public IP")
        print("      -mac <mac>        - Filter by MAC address")
        print("      -s <state>        - Filter by state (active/inactive)")
        print("  n, next           - Show next page")
        print("  b, back, prev     - Show previous page")
        print("  u, update         - Update all machine data")
        print("  o, online         - Update only online machines (more efficient)")
        print("  h, help           - Show this help")
        print("  q, quit, e, exit     - Exit the program")
        print("  t, templates     - List valid tunnel templates")
        print("    Options:")
        print("      -type <0,1,2,5>    - Tunnel type (TCP/HTTP/HTTPS/UDP)")
        print("      -t <0,3,254,255>   - Template type")
        print("      -b <1-24>          - Bandwidth in Mbps")
        print("  ssh <machine_name>  - Create SSH tunnel for a machine")
        print("  connect <machine_name>  - Create tunnel for a machine to specific port")
        print("    Options:")
        print("      -port <port number> - Specific port number (mandatory)")
        print("  analyze, dns      - Perform reverse DNS lookup")
        print("  export, csv [filename] - Export all data to CSV file")
        print("\nExample: p -m raspberrypi -s active")

    def parse_filters(self, args):
        filters = {}
        i = 0
        while i < len(args):
            if args[i].startswith('-'):
                if i + 1 < len(args):
                    key = args[i][1:]
                    value = args[i + 1]
                    filters[key] = value
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        return filters

    def apply_filters(self, query, filters):
        conditions = []
        params = []
        
        if 'm' in filters:  # machine name filter
            conditions.append("name LIKE ?")
            params.append(f"%{filters['m']}%")
            
        if 'i' in filters:  # IP filter
            conditions.append("(ip LIKE ? OR public_ip LIKE ?)")
            params.extend([f"%{filters['i']}%", f"%{filters['i']}%"])
            
        if 'mac' in filters:  # MAC address filter
            conditions.append("mac LIKE ?")
            params.append(f"%{filters['mac']}%")
            
        if 's' in filters:  # state filter
            state_map = {'active': 1, 'inactive': 0}
            if filters['s'].lower() in state_map:
                conditions.append("is_active = ?")
                params.append(state_map[filters['s'].lower()])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        return query, params

    def get_total_records(self, filters):
        query = "SELECT COUNT(*) as count FROM machines"
        query, params = self.apply_filters(query, filters)
        
        with sqlite3.connect(self.api.db.db_path) as conn:
            result = conn.execute(query, params).fetchone()
            return result[0]

    def print_tunnels(self, *args):
        if args:  # If new filters provided, reset to first page
            self.current_filters = self.parse_filters(args)
            self.current_page = 0
            # Only print total count on initial display or filter change
            with sqlite3.connect(self.api.db.db_path) as conn:
                total_count = conn.execute("SELECT COUNT(*) FROM machines").fetchone()[0]
                print(f"Total machines in database: {total_count}")

        self.display_current_page(clear_screen=False)  # Don't clear on first display
        self.handle_pagination()

    def display_current_page(self, clear_screen=True):
        if clear_screen:
            print("\033[2J\033[H", end='')

        machines, total_records = self.api.db.get_machines_for_display(
            page=self.current_page,
            page_size=self.page_size,
            filters=self.current_filters
        )
        
        total_pages = (total_records + self.page_size - 1) // self.page_size
        
        if not machines:
            print("\nNo machines found matching the filters.")
            return

        print(f"\n=== Current Machines (Page {self.current_page + 1}/{total_pages}) ===")
        print(f"{'ID':<36} {'Name':<15} {'OS':<15} {'IP':<15} {'Public IP':<15} {'MAC':<18} {'Organization':<20} {'Status':<10} {'Last Active':<12}")
        print("-" * 165)

        for machine in machines:
            status = "Active" if machine['is_active'] == 1 else "Inactive"
            active_time = machine['active_time'].split('T')[0] if machine['active_time'] else 'N/A'
            org = machine['dns_hostname'][:19] if machine['dns_hostname'] else 'N/A'
            mac = machine['mac'][:17] if machine['mac'] else 'N/A'
            os_val = machine['os'][:14] if machine['os'] else 'N/A'
            
            print(f"{machine['id']:<36} {machine['name'][:14]:<15} {os_val:<15} {machine['ip'][:14]:<15} "
                  f"{machine['public_ip'][:14]:<15} {mac:<18} {org:<20} {status:<10} {active_time:<12}")
        
        print(f"\nShowing {self.current_page * self.page_size + 1}-{min((self.current_page + 1) * self.page_size, total_records)} of {total_records} records")
        print("Use 'n' for next page, 'b' for previous page, 'q' to return to command mode", end='\r')

    def handle_pagination(self):
        with KeyboardListener() as listener:
            self.keyboard_listener = listener
            while not listener.should_stop:
                if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    if char == 'n':
                        self.next_page(silent=True)
                    elif char == 'b':
                        self.prev_page(silent=True)
                    elif char == 'q':
                        break

    def next_page(self, *args, silent=False):
        total_records = self.get_total_records(self.current_filters)
        total_pages = (total_records + self.page_size - 1) // self.page_size
        
        if self.current_page < total_pages - 1:
            self.current_page += 1
            if silent:
                self.display_current_page()
            else:
                self.print_tunnels()
        else:
            print("\rAlready at the last page.", end='')

    def prev_page(self, *args, silent=False):
        if self.current_page > 0:
            self.current_page -= 1
            if silent:
                self.display_current_page()
            else:
                self.print_tunnels()
        else:
            print("\rAlready at the first page.", end='')

    def update_data(self, *args):
        print("\nStarting data update...")
        self.api.start_background_update()
        
        while self.api.is_updating:
            try:
                status = self.api.update_queue.get(timeout=0.5)
                print(status, end='', flush=True)
            except queue.Empty:
                continue
                
        # After update is complete, automatically show active machines
        print("\n\nShowing active machines:")
        self.current_filters = {'s': ''} 
        # self.current_page = 0  # Reset to first page
        # self.print_tunnels()

    def update_online_machines(self, *args):
        """Update only machines that are currently online"""
        print("\nStarting online machines update...")
        self.api.start_online_machines_update()
        
        while self.api.is_updating:
            try:
                status = self.api.update_queue.get(timeout=0.5)
                print(status, end='', flush=True)
            except queue.Empty:
                continue
                
        # After update is complete, automatically show active machines
        print("\n\nShowing active machines:")
        self.current_filters = {'s': 'active'}  # Set filter for active machines
        self.current_page = 0  # Reset to first page
        self.print_tunnels()
        self.current_filters = {'s': ''} # Reset filter

    def exit(self, *args):
        self.running = False
        return True

    def run(self):
        print("\nWelcome to Bin4rys Unitree Tunnel Manager")
        print("Type 'help' for available commands")
        
        while self.running:
            try:
                cmd = input("\n> ").strip().split()
                if not cmd:
                    continue
                
                command = cmd[0].lower()
                args = cmd[1:]
                
                if command in self.commands:
                    self.commands[command](*args)
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to exit properly")
            except Exception as e:
                print(f"Error: {e}")

    def list_templates(self, *args):
        """List valid tunnel templates with optional filtering"""
        if not args:
            print("\nError: Tunnel type is required")
            print("Usage: t -type <0,1,2,5> [-t <template_type>] [-b <bandwidth>]")
            print("\nTunnel types:")
            print("  0: TCP")
            print("  1: HTTP")
            print("  2: HTTPS")
            print("  5: UDP")
            return

        # Parse arguments
        filters = self.parse_filters(args)
        
        if 'type' not in filters:
            print("\nError: Tunnel type (-type) is required")
            return

        try:
            tunnel_type = int(filters['type'])
            template_type = int(filters['t']) if 't' in filters else None
            bandwidth = int(filters['b']) if 'b' in filters else None
        except ValueError:
            print("\nError: All parameters must be numbers")
            return

        response = self.api.list_valid_templates(tunnel_type, template_type, bandwidth)
        
        if response.get('error', 1) != 0:
            print(f"\nError fetching templates: {response.get('info', 'Unknown error')}")
            return

        templates = response.get('data', [])
        total = response.get('total', 0)

        if not templates:
            print("\nNo templates found matching the criteria")
            return

        print(f"\n=== Valid Templates (Total: {total}) ===")
        print(f"{'ID':<36} {'Type':<8} {'Bandwidth':<10} {'Concurrent':<10} {'Domain':<8} {'Expires':<12}")
        print("-" * 90)

        for template in templates:
            template_type = {
                0: "Random",
                3: "Same",
                254: "5¥ Free",
                255: "Free"
            }.get(template.get('type'), "Unknown")

            print(f"{template['id']:<36} "
                  f"{template_type:<8} "
                  f"{template.get('bandwidth', 'N/A'):<10} "
                  f"{template.get('concurrency', 'N/A'):<10} "
                  f"{('Yes' if template.get('domain') == 1 else 'No'):<8} "
                  f"{template.get('expiresIn', 'N/A')} days")

    def create_ssh_access(self, *args):
        """Create an SSH tunnel for a specific machine"""
        if not args:
            print("\nError: Machine ID is required")
            print("Usage: ssh <machine_id>")
            return

        # Parse machine ID and options
        machine_id = args[0]
        template_id = None
        # Find the machine
        query = "SELECT * FROM machines WHERE id = ?"
        with sqlite3.connect(self.api.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            machine = conn.execute(query, [machine_id]).fetchone()

        if not machine:
            print(f"\nNo machine found with ID: {machine_id}")
            return

        print("\nFetching available TCP templates...")
        response = self.api.list_valid_templates(
            tunnel_type=0,  # TCP
        )
        # print(response)
        # return 
        if response.get('error', 1) != 0:
            print(f"\nError fetching templates: {response.get('info', 'Unknown error')}")
            return

        templates = response.get('data', [])
        if not templates:
            print("\nNo valid TCP templates found. Will create a new template.")
        else:
            template_id = templates[0]['id']  # Use first available template

        # Create the tunnel
        print(f"\nCreating SSH tunnel for {machine['name']} (ID: {machine['id']}) to port 22")

        response = self.api.create_tunnel(
            machine_id=machine['id'],
            template_id=template_id,
            port=22
        )

        if response.get('error', 1) != 0:
            print(f"\nError creating tunnel: {response.get('info', 'Unknown error')}")
            return

        tunnel_data = response.get('data', {})
        print("\nSSH Tunnel created successfully!")
        print(f"Remote Domain: {tunnel_data.get('domain', 'N/A')}")
        print(f"Remote Address: {tunnel_data.get('host', 'N/A')}")
        print(f"Remote Port: {tunnel_data.get('port', 'N/A')}")
        print(f"Remote id: {tunnel_data.get('id', 'N/A')}")
        print("\nConnect using:")
        print(f"ssh -p {tunnel_data.get('port', 'N/A')} pi@{tunnel_data.get('host', 'N/A')}")

    def create_tunnel_to_port(self, *args):
        """Create a tunnel for a specific machine to a specific port"""
        if not args:
            print("\nError: Machine ID and port number are required")
            print("Usage: connect <machine_id> -port <port_number>")
            return
        
        # Parse machine ID and options
        machine_id = args[0]
        
        # Parse the arguments using the existing parse_filters method
        filters = self.parse_filters(args[1:])
        
        # Check if port is specified
        if 'port' not in filters:
            print("\nError: Port specification is required")
            print("Usage: connect <machine_id> -port <port_number>")
            return
            
        port = filters['port']
        
        template_id = None
        # Find the machine
        query = "SELECT * FROM machines WHERE id = ?"
        with sqlite3.connect(self.api.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            machine = conn.execute(query, [machine_id]).fetchone()

        if not machine:
            print(f"\nNo machine found with ID: {machine_id}")
            return

        print("\nFetching available TCP templates...")
        response = self.api.list_valid_templates(
            tunnel_type=0,  # TCP
        )
        
        if response.get('error', 1) != 0:
            print(f"\nError fetching templates: {response.get('info', 'Unknown error')}")
            return

        templates = response.get('data', [])
        if not templates:
            print("\nNo valid TCP templates found. Will create a new template.")
        else:
            template_id = templates[0]['id']  # Use first available template
            
        # Create the tunnel
        print(f"\nCreating tunnel for {machine['name']} (ID: {machine['id']}) to port {port}")

        response = self.api.create_tunnel(
            machine_id=machine['id'],
            template_id=template_id,
            port=port
        )

        if response.get('error', 1) != 0:
            print(f"\nError creating tunnel: {response.get('info', 'Unknown error')}")
            return

        tunnel_data = response.get('data', {})
        print("\nTunnel created successfully!")
        print(f"Remote Domain: {tunnel_data.get('domain', 'N/A')}")
        print(f"Remote Address: {tunnel_data.get('host', 'N/A')}")
        print(f"Remote Port: {tunnel_data.get('port', 'N/A')}")
        print(f"Remote id: {tunnel_data.get('id', 'N/A')}")

    def analyze_organizations(self, *args):
        """Analyze organizations using reverse DNS lookups"""
        self.api.db.analyze_organizations()

    def export_to_csv(self, *args):
        """Export all machine data to CSV file"""
        filename = 'unitree_machines.csv'
        if args:
            filename = args[0]
        if not filename.endswith('.csv'):
            filename += '.csv'

        headers = [
            # Basic machine info
            'ID', 'Name', 'OS', 'IP', 'Public IP', 'MAC', 'Version',
            'Status', 'Last Active', 'Added', 'Last Updated',
            # DNS lookup fields - exactly matching database columns
            'dns_hostname',
            'dns_status',
            'dns_country',
            'dns_city',
            'dns_org',
            'dns_isp',
            'dns_asn',
            'dns_is_mobile',
            'dns_is_proxy',
            'dns_is_hosting',
            'dns_last_lookup'
        ]

        print(f"\nExporting data to {filename}...")
        
        try:
            with sqlite3.connect(self.api.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                machines = conn.execute("""
                    SELECT * FROM machines 
                    ORDER BY active_time DESC NULLS LAST
                """).fetchall()

                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    
                    for machine in machines:
                        writer.writerow([
                            machine['id'],
                            machine['name'],
                            machine['os'],
                            machine['ip'],
                            machine['public_ip'],
                            machine['mac'],
                            machine['version'],
                            'Active' if machine['is_active'] == 1 else 'Inactive',
                            machine['active_time'],
                            machine['add_time'],
                            machine['last_updated'],
                            # DNS fields - exactly matching database columns
                            machine['dns_hostname'],
                            machine['dns_status'],
                            machine['dns_country'],
                            machine['dns_city'],
                            machine['dns_org'],
                            machine['dns_isp'],
                            machine['dns_asn'],
                            machine['dns_is_mobile'],
                            machine['dns_is_proxy'],
                            machine['dns_is_hosting'],
                            machine['dns_last_lookup']
                        ])

            total_records = len(machines)
            print(f"Successfully exported {total_records} records to {filename}")

        except Exception as e:
            print(f"Error exporting data: {e}")

def main():
    API_KEY = "206a70fb105798954096c6603fff2af1"
    api = ZhexiAPI(API_KEY)
    shell = InteractiveShell(api)
    shell.run()

if __name__ == "__main__":
    main()
