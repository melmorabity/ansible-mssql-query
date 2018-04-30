# mssql_query

Run a SQL query on a Microsoft SQL Server database.

## Synopsis
 Run a SQL query on a Microsoft SQL Server database.

## Options

| parameter      | required | default | choices | comments                                                                                                                                                                |
| -------------- | -------- | ------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| autocommit     | no       | False   |         | Automatically commit the change only if the import succeed. Sometimes it is necessary to use autocommit=true, since some content can't be changed within a transaction. |
| login_user     | no       |         |         | The username used to authenticate with.                                                                                                                                 |
| login_host     | no       |         |         | The host running the database.                                                                                                                                          |
| as_dict        | no       | False   |         | If true, return results as a list of dictionaries.                                                                                                                      |
| db             | no       |         |         | The name of the database.                                                                                                                                               |
| login_password | no       |         |         | The password used to authenticate with.                                                                                                                                 |
| query          | yes      |         |         | The SQL query to run.                                                                                                                                                   |
| port           | no       | 1433    |         | The database port to connect to.                                                                                                                                        |
| tds_version    | no       | 7.1     |         | The TDS protocol version to use.                                                                                                                                        |

## Examples

```
# Run SQL query
- local_action:
    module: mssql_query
    db: mydatabase
    query: SELECT * FROM myschema.mytable
```

## Notes

* Requires the pymssql Python package on the remote host.
