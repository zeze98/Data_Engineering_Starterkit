{
    'table': 'mau_summary',
    'schema': 'jaewoo98y',
    'main_sql': """SELECT 
  TO_CHAR(A.ts, 'YYYY-MM') AS month,
  COUNT(DISTINCT B.userid) AS mau
FROM raw_data.session_timestamp A
JOIN raw_data.user_session_channel B ON A.sessionid = B.sessionid
GROUP BY 1 
;""",
    'input_check':
    [
              {
                  'sql': 'SELECT COUNT(1) FROM jaewoo98y.nps',
                  'count': 150000
              },
    ],
    'output_check':
    [
        {
            'sql': 'SELECT COUNT(1) FROM {schema}.temp_{table}',
            'count': 12
        }
    ],
}
