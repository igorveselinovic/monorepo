{{ config(materialized='table') }}

select
  events.id                                as unlock_event_id,
  events.starttime                         as unlock_event_timestamp

from
  {{ source('activity_watch', 'events') }} as events
left join
  {{ source('activity_watch', 'buckets') }} as buckets
on
  events.bucketrow = buckets.id

where
  buckets.type = 'os.lockscreen.unlocks'
