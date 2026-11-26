{{ config(materialized='table') }}

with events as (
  select
    events.id                            as unlock_event_id,
    events.starttime                     as unlock_event_unix_timestamp,
    cast(
      datetime(
        events.starttime / 1000000000.0,
        'unixepoch',
        'subsec'
      ) as text
    )                                    as unlock_event_timestamp

  from
    {{ ref('base_events') }} as events
  left join
    {{ source('activity_watch', 'buckets') }} as buckets
  on
    events.bucketrow = buckets.id

  where
    buckets.type = 'os.lockscreen.unlocks'
)

select
  unlock_event_id,
  unlock_event_unix_timestamp,
  unlock_event_timestamp,
  datetime(unlock_event_timestamp, 'localtime', 'subsec') as unlock_event_timestamp_local

from events

