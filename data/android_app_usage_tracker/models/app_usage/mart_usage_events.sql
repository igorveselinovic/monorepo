{{ config(materialized='table') }}

select
  id                                as usage_event_id,
  starttime                         as usage_event_starttime,
  endtime                           as usage_event_endtime,
  json_extract(data, '$.app')       as app_name,
  json_extract(data, '$.package')   as app_package_name,
  json_extract(data, '$.classname') as app_class_name

from
  {{ source('activity_watch', 'events') }}

where
  bucketrow != 3
