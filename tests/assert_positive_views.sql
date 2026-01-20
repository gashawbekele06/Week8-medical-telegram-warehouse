-- Must return 0 rows
select *
from {{ ref('fct_messages') }}
where view_count < 0