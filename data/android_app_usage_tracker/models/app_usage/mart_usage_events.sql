{{ config(materialized='table') }}

with events as (
  select
    events.id                                              as usage_event_id,
    events.starttime                                       as usage_event_start_unix_timestamp,
    cast(
      datetime(
        events.starttime / 1000000000.0,
        'unixepoch',
        'subsec'
      ) as text
    )                                                      as usage_event_start_timestamp,
    events.endtime                                         as usage_event_end_unix_timestamp,
    cast(
      datetime(
        events.endtime / 1000000000.0,
        'unixepoch',
        'subsec'
      ) as text
    )                                                      as usage_event_end_timestamp,
    cast(events.endtime - events.starttime as int)         as usage_event_duration_nanoseconds,
    cast(json_extract(events.data, '$.app') as text)       as app_name,
    cast(json_extract(events.data, '$.package') as text)   as app_package_name,
    cast(json_extract(events.data, '$.classname') as text) as app_class_name

  from
    {{ ref('base_events') }} as events
  left join
    {{ source('activity_watch', 'buckets') }} as buckets
  on
    events.bucketrow = buckets.id

  where
    buckets.type = 'currentwindow'
)

select
  usage_event_id,
  usage_event_start_unix_timestamp,
  usage_event_start_timestamp,
  datetime(usage_event_start_timestamp, 'localtime', 'subsec')         as usage_event_start_timestamp_local,
  usage_event_end_unix_timestamp,
  usage_event_end_timestamp,
  datetime(usage_event_end_timestamp, 'localtime', 'subsec')           as usage_event_end_timestamp_local,
  usage_event_duration_nanoseconds,
  cast(usage_event_duration_nanoseconds / 1000000 as int)              as usage_event_duration_milliseconds,
  cast(usage_event_duration_nanoseconds / 1000000000.0 as real)        as usage_event_duration_seconds,
  cast(usage_event_duration_nanoseconds / 1000000000.0 / 60 as real)   as usage_event_duration_minutes,
  cast(usage_event_duration_nanoseconds / 1000000000.0 / 3600 as real) as usage_event_duration_hours,
  app_name,
  app_package_name,
  app_class_name

from events
