# Publish Events

## Milestones

The following is an ordered sequence of events for publish.

```
  provide_started_at: datetime
  find_node_started_at: Optional[datetime]
  dht_walk_ended_at: Optional[datetime]
  provide_ended_at: Optional[datetime]
  get_providers_ended_at: Optional[datetime]
```

## Phases

```
  INITIATED = 1
  GETTING_CLOSEST_PEERS = 2
  PUTTING_GETTING_PROVIDER_RECORDS = 3
  DONE = 4
```

## Phase -> Milestone Mapping

```
{
  INITIATED: provide_started_at,
  GETTING_CLOSEST_PEERS: find_node_started_at,
  PUTTING_GETTING_PROVIDER_RECORDS: dht_walk_ended_at,
  DONE: provide_ended_at
}
```

## Phase Latency Calculations

```
{
  INITIATED: find_node_started_at-provide_started_at,
  GETTING_CLOSEST_PEERS: dht_walk_ended_at-find_node_started_at,
  PUTTING_GETTING_PROVIDER_RECORDS: get_providers_ended_at-dht_walk_ended_at,
  DONE: provide_ended_at-get_providers_ended_at
}
```

## Milestone -> Log Mapping

```
{
  provide_started_at: "{TIMESTAMP}: Start providing cid {CID}",
  find_node_started_at: "{TIMESTAMP}: Start getting closest peers to cid {CID}",
  dht_walk_ended_at: "${TIMESTAMP}: In total, got \d+ closest peers to cid {CID}: {CLOSEST_PEER_IDS}",
  provide_ended_at: "{TIMESTAMP}: Succeed in putting provider record for cid {CID} to {CLOSEST_PEER_ID}({CLOSEST_PEER_AGENT})" | "{TIMESTAMP}: Error putting provider record for cid {CID} to {CLOSEST_PEER_ID}({CLOSEST_PEER_AGENT}) [{ERROR_STR}]",
  get_providers_ended_at: "{TIMESTAMP}: Finish providing cid {CID}"
}
