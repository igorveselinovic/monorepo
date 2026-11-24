{{ config(materialized='table') }}

select
  events.id                                              as usage_event_id,
  events.starttime                                       as usage_event_start_timestamp,
  events.endtime                                         as usage_event_end_timestamp,
  cast(json_extract(events.data, '$.app') as text)       as app_name,
  cast(json_extract(events.data, '$.package') as text)   as app_package_name,
  cast(json_extract(events.data, '$.classname') as text) as app_class_name

from
  {{ source('activity_watch', 'events') }} as events
left join
  {{ source('activity_watch', 'buckets') }} as buckets
on
  events.bucketrow = buckets.id

where
  buckets.type = 'currentwindow'
