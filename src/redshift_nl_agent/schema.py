#!/usr/bin/env python3
"""
Schema Context Manager for Redshift Agent
Loads and manages database schema information for LLM context
"""
import json
import os
import re
import time
from pathlib import Path
from datetime import datetime, timedelta
from .database import RedshiftCLI


class SchemaContext:
    """Manages database schema context for natural language queries"""

    def __init__(self, cli):
        self.cli = cli
        self.schema_cache = {}
        self.table_list = []
        self.cache_dir = Path.home() / ".redshift_agent"
        self.cache_file = self.cache_dir / "schema_cache.json"
        self.cache_ttl = timedelta(hours=24)
        self._load_schema()

    def _load_schema(self):
        """Load schema information (from cache or database)"""
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Try to load from cache
        if self._load_from_cache():
            print(f"✓ Schema loaded from cache ({len(self.table_list)} tables)")
            return

        print("Loading schema context from database...")
        self.refresh_schema()

    def _load_from_cache(self):
        """Load schema from persistent cache"""
        if not self.cache_file.exists():
            return False

        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)

            # Check if cache is expired
            cached_time = datetime.fromisoformat(data.get('timestamp'))
            if datetime.now() - cached_time > self.cache_ttl:
                print("Schema cache expired")
                return False

            self.table_list = data.get('table_list', [])
            self.schema_cache = data.get('schema_cache', {})
            return True
        except Exception as e:
            print(f"Failed to load cache: {e}")
            return False

    def _save_to_cache(self):
        """Save schema to persistent cache"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'table_list': self.table_list,
                'schema_cache': self.schema_cache
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Failed to save cache: {e}")

    def refresh_schema(self):
        """Force refresh of schema from database"""
        # Get list of core tables
        result = self.cli.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)

        if result and not isinstance(result, str):
            all_tables = [r[0] for r in result]
            self.table_list = [t for t in all_tables if self._is_core_table(t)]
            print(f"Loaded {len(self.table_list)} core tables")

            # Batch fetch columns for all core tables
            self._batch_fetch_columns()
            self._save_to_cache()

    def _batch_fetch_columns(self):
        """Fetch columns for all tables in a single query"""
        print("Batch fetching columns...")
        
        # Build a list of tables to fetch
        tables_str = "', '".join(self.table_list)
        
        query = f"""
            SELECT
                c.relname as table_name,
                a.attname as column_name,
                format_type(a.atttypid, a.atttypmod) as data_type,
                CASE WHEN a.attnotnull THEN 'NOT NULL' ELSE 'NULL' END as nullable
            FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE n.nspname = 'public'
            AND c.relname IN ('{tables_str}')
            AND a.attnum > 0
            AND NOT a.attisdropped
            ORDER BY c.relname, a.attnum
        """
        
        result = self.cli.execute(query)
        
        if result and not isinstance(result, str):
            # Group by table
            current_table = None
            columns = []
            
            for row in result:
                table_name = row[0]
                col_info = {
                    'name': row[1],
                    'type': row[2],
                    'nullable': row[3]
                }
                
                if table_name != current_table:
                    if current_table:
                        self.schema_cache[current_table] = {
                            'table_name': current_table,
                            'columns': columns
                        }
                    current_table = table_name
                    columns = []
                
                columns.append(col_info)
            
            # Add last table
            if current_table:
                self.schema_cache[current_table] = {
                    'table_name': current_table,
                    'columns': columns
                }

    def _is_core_table(self, table_name):
        """Determine if table is a core table vs temporary/staging"""
        # Exclude tables with no user permissions
        restricted_tables = ['fact_device_status_weekly']
        if table_name in restricted_tables:
            return False

        if 'temp' in table_name.lower() or '_test' in table_name.lower():
            return False
        if re.search(r'_\d{8,}', table_name):
            return False
        if re.search(r'_\d{4}(_\d{2})?$', table_name):
            return False
        return True

    def get_table_schema(self, table_name):
        """Get detailed schema for a specific table"""
        return self.schema_cache.get(table_name)

    def get_relevant_tables(self, query_text):
        """
        Identify relevant tables based on query keywords
        Returns list of table names
        """
        query_lower = query_text.lower()
        relevant = []

        # Keyword mapping to tables
        keywords_map = {
            'camera': ['camera_info', 'ods_camera_info_f', 'ods_camera_configure_f',
                      'ods_camera_event_f', 'ods_camera_running_info_f'],
            'event': ['ods_camera_event_f', 'ods_camera_event_f_gpst', 'ods_camera_event_f_security'],
            'fleet': ['fleet_info', 'fleet_info_staging', 'ods_fleet_info_f', 'prod_fleet_name'],
            'device': ['device_daily_report_data'],
            'clip': ['ods_clip_f', 'ods_clip_request_f', 'ods_original_clip_f'],
            'gps': ['ods_gps_f', 'ods_redis_camera_all_lastgps_f'],
            'firmware': ['ods_firmware_f', 'ods_firmware_upgrade_trail_f', 'prod_firmware_update_audit_log'],
            'data usage': ['fact_data_usage_volume_daily', 'fact_data_usage_volume_weekly', 'fact_data_usage_volume_monthly'],
            'status': ['ods_camera_running_info_f', 'ods_redis_camera_all_status_f', 'prod_sim_status'],
            'location': ['ods_camera_running_info_location', 'ods_gps_f'],
            'trip': ['fact_device_trip_details_weekly', 'ods_tb_closed_ziptrip_f'],
        }

        # Find matching tables
        for keyword, tables in keywords_map.items():
            if keyword in query_lower:
                for table in tables:
                    if table in self.table_list and table not in relevant:
                        relevant.append(table)

        # If no specific keywords found, return most common tables
        if not relevant:
            relevant = [
                'ods_camera_info_f',
                'ods_camera_event_f',
                'ods_camera_running_info_f',
                'fleet_info',
                'ods_gps_f'
            ]
            relevant = [t for t in relevant if t in self.table_list]

        return relevant[:10]  # Limit to 10 tables

    def build_context_for_llm(self, query_text):
        """
        Build schema context string for LLM prompt
        Only includes relevant tables based on query
        """
        relevant_tables = self.get_relevant_tables(query_text)

        context_parts = [
            "# Database Schema Context",
            "",
            "## Database Information",
            "- Database: prod (Redshift)",
            "- Schema: public",
            "- System: Camera/Dashcam Fleet Management",
            "",
            "## Available Tables",
            ""
        ]

        # Add schema for each relevant table
        for table_name in relevant_tables:
            schema = self.get_table_schema(table_name)
            if schema:
                # Filter out technical columns
                columns = [
                    f"{col['name']}({col['type']})"
                    for col in schema['columns']
                    if not self._is_technical_column(col['name'])
                ]
                # Compact format: TableName: col1(type), col2(type)...
                context_parts.append(f"- **{table_name}**: {', '.join(columns)}")

        # Add common patterns and naming conventions
        context_parts.extend([
            "",
            "## Naming Conventions",
            "- `ods_*`: Operational Data Store (raw)",
            "- `fact_*`: Analytical fact tables",
            "- `prod_*`: Production views",
            "- `_f`: Fact tables",
            "",
            "## Important Notes",
            "- Date cols: created_at, updated_at, timestamp, date",
            "- ID cols: id, camera_id, device_id, fleet_id",
            "- Use schema prefix: public.tablename",
            ""
        ])

        return "\n".join(context_parts)

    def _is_technical_column(self, col_name):
        """Check if column is a technical/system column that can be hidden"""
        technical_prefixes = ['etl_', 'dms_', 'cdc_']
        technical_suffixes = ['_audit', '_checksum']
        technical_exact = ['created_by', 'updated_by', 'last_updated_by', 'row_id', 'batch_id']
        
        col_lower = col_name.lower()
        
        if col_lower in technical_exact:
            return True
            
        for prefix in technical_prefixes:
            if col_lower.startswith(prefix):
                return True
                
        for suffix in technical_suffixes:
            if col_lower.endswith(suffix):
                return True
                
        return False

    def get_full_schema_summary(self):
        """Get a summary of all tables (for /schema command)"""
        summary = ["# Database Schema Summary", ""]

        # Group tables by prefix
        fact_tables = [t for t in self.table_list if t.startswith('fact_')]
        prod_tables = [t for t in self.table_list if t.startswith('prod_')]
        ods_tables = [t for t in self.table_list if t.startswith('ods_')]
        camera_tables = [t for t in self.table_list if t.startswith('camera_')]
        device_tables = [t for t in self.table_list if t.startswith('device_')]
        fleet_tables = [t for t in self.table_list if t.startswith('fleet_')]
        other_tables = [t for t in self.table_list
                       if not any(t.startswith(p) for p in ['fact_', 'prod_', 'ods_', 'camera_', 'device_', 'fleet_'])]

        if fact_tables:
            summary.append(f"## Fact Tables ({len(fact_tables)})")
            for t in fact_tables[:20]:
                summary.append(f"  - {t}")
            summary.append("")

        if prod_tables:
            summary.append(f"## Production Tables ({len(prod_tables)})")
            for t in prod_tables[:20]:
                summary.append(f"  - {t}")
            summary.append("")

        if ods_tables:
            summary.append(f"## ODS Tables ({len(ods_tables)})")
            summary.append(f"  (Showing first 20 of {len(ods_tables)})")
            for t in ods_tables[:20]:
                summary.append(f"  - {t}")
            summary.append("")

        if camera_tables:
            summary.append(f"## Camera Tables ({len(camera_tables)})")
            for t in camera_tables:
                summary.append(f"  - {t}")
            summary.append("")

        if device_tables:
            summary.append(f"## Device Tables ({len(device_tables)})")
            for t in device_tables:
                summary.append(f"  - {t}")
            summary.append("")

        if fleet_tables:
            summary.append(f"## Fleet Tables ({len(fleet_tables)})")
            for t in fleet_tables:
                summary.append(f"  - {t}")
            summary.append("")

        if other_tables:
            summary.append(f"## Other Tables ({len(other_tables)})")
            for t in other_tables:
                summary.append(f"  - {t}")
            summary.append("")

        return "\n".join(summary)
