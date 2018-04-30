#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2017-2018 Mohamed El Morabity
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not,
# see <http://www.gnu.org/licenses/>.


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.parsing.convert_bool import BOOLEANS


DOCUMENTATION = '''
---
module: mssql_query
author: Mohamed El Morabity
short_description: Run a SQL query on a Microsoft SQL Server database.
description:
  - Run a SQL query on a Microsoft SQL Server database.
options:
  login_user:
    description:
      - The username used to authenticate with.
    required: false
    default: ''
  login_password:
    description:
      - The password used to authenticate with.
    required: false
    default: ''
  login_host:
    description:
      - The host running the database.
    required: false
    default: ''
  port:
    description:
      - The database port to connect to.
    type: int
    required: false
    default: 1433
    aliases: ['login_port']
  db:
    description:
      - The name of the database.
    required: false
    default: ''
  query:
    description:
      - The SQL query to run.
    required: True
  autocommit:
    description:
      - Automatically commit the change only if the import succeed. Sometimes it is necessary to use autocommit=true, since some content can't be changed within a transaction.
    required: false
    default: false
  tds_version:
    description:
      - The TDS protocol version to use.
    required: false
    default: 7.1
  as_dict:
    description:
      - If true, return results as a list of dictionaries.
    type: bool
    required: false
    default: false
notes:
  - Requires the pymssql Python package on the remote host.
requirements: ['pymssql']
'''

EXAMPLES = '''
# Run SQL query
- local_action:
    module: mssql_query
    db: mydatabase
    query: SELECT * FROM myschema.mytable
'''


try:
    import pymssql

    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def run_query(module, db_connection, as_dict):
    """Run a SQL query."""

    query = module.params['query']

    result = []
    try:
        cursor = db_connection.cursor(as_dict=as_dict)
        cursor.execute(query)
        try:
            result = cursor.fetchall()
        except pymssql.OperationalError as ex:
            if 'Statement not executed or executed statement has no resultset' in ex.args:
                pass
        changed = cursor.rowcount != 0
        db_connection.commit()
        cursor.close()
    except pymssql.ColumnsWithoutNamesError as ex:
        # If no column name in result, re-run without as dict
        return run_query(module, db_connection, False)
    except pymssql.Error as ex:
        if ex.args:
            module.fail_json(msg='Unable to execute query: {}'.format(ex[1]), errno=ex[0])
        module.fail_json(msg='Unable to execute query: {}'.format(ex))
    finally:
        if db_connection is not None:
            db_connection.close()

    return (changed, result, cursor.rowcount)


def main():
    """Main execution path."""

    module = AnsibleModule(
        argument_spec={
            'login_host': {'type': 'str', 'default': ''},
            'port': {'type': 'int', 'default': 1433, 'aliases': ['login_port']},
            'login_user': {'type': 'str', 'default': ''},
            'login_password': {'type': 'str', 'default': '', 'no_log': True},
            'query': {'required': True, 'type': 'str'},
            'db': {'type': 'str', 'default': ''},
            'autocommit': {'type': 'bool', 'choices': BOOLEANS, 'default': False},
            'tds_version': {'type': 'str', 'default': '7.1'},
            'as_dict': {'type': 'bool', 'choices': BOOLEANS, 'default': False},
        }
    )

    if not HAS_LIB:
        module.fail_json(msg='pymssql is required for this module')

    try:
        db_connection = pymssql.connect(host=module.params['login_host'],
                                        port=str(module.params['port']),
                                        user=module.params['login_user'],
                                        password=module.params['login_password'],
                                        database=module.params['db'],
                                        tds_version=module.params['tds_version'])
        db_connection.autocommit(module.params['autocommit'])
    except pymssql.Error as ex:
        module.fail_json(msg='Unable to connect to database: {}'.format(ex))

    (changed, result, rowcount) = run_query(module, db_connection,
                                            as_dict=module.params['as_dict'])

    module.exit_json(changed=changed, result=result, rowcount=rowcount)


if __name__ == '__main__':
    main()
