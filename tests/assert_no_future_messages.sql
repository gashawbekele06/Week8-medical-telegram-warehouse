-- Must return 0 rows to pass
select *
from {{ ref('fct_messages') }}
where message_timestamp > current_timestamp