select
  id,
  bucketrow,
  starttime,
  endtime,
  data

from
  {{ source('activity_watch', 'events') }} as events

group by
  bucketrow,
  starttime,
  endtime,
  data
