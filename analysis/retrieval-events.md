# Retrieval Events

## Milestones

The following is an ordered sequence of events for retrieval.

```
  retrieval_started_at: datetime
  get_providers_queries_started_at: Optional[datetime]
  found_first_provider_at: Optional[datetime]
  dial_started_at: Optional[datetime]
  connected_at: Optional[datetime]
  stream_opened_at: Optional[datetime]
  # there could be more than one provider
  received_first_HAVE_at: Optional[datetime]
  done_retrieving_at: Optional[datetime]
  finished_searching_providers_at: Optional[datetime]
```

## Phases

```
  INITIATED = 1
  GETTING_CLOSEST_PEERS = 2
  DIALING = 3
  FETCHING = 4
  DONE = 5
  DONE_WITHOUT_ASKING_PEERS = 6
```

## Phase -> Milestone Mapping

```
{
  INITIATED: retrieval_started_at,
  GETTING_CLOSEST_PEERS: get_providers_queries_started_at,
  DIALING: dial_started_at,
  FETCHING: connected_at,
  DONE: done_retrieving_at | finished_searching_providers_at
  DONE_WITHOUT_ASKING_PEERS: done_retrieving_at | finished_searching_providers_at
}
```

## Phase Latency Calculations

```
{
  INITIATED: get_providers_queries_started_at - retrieval_started_at
  GETTING_CLOSEST_PEERS: dial_started_at - get_providers_queries_started_at,
  DIALING: connected_at - dial_started_at,
  FETCHING: done_retrieving_at - connected_at,
  DONE: done_retrieving_at | finished_searching_providers_at
}
```

## Milestone -> Log Mapping

```
{
  retrieval_started_at: "${TIMESTAMP}: Start retrieving content for ${CID}",
  get_providers_queries_started_at: "${TIMESTAMP}: Start searching providers for cid ${CID}",
  found_first_provider_at: "${TIMESTAMP}: Found provider ${PROVIDER_PEER_ID} for cid ${CID} from ${REMOTE_PEER_ID}(${REMOTE_PEER_AGENT})",
  dial_started_at: "${TIMESTAMP}: Bitswap connect to peer ${PROVIDER_PEER_ID}",
  connected_at: "${TIMESTAMP}: Connected to provider ${PROVIDER_PEER_ID}(${PROVIDER_AGENT}) for cid ${CID} from ${POINTER_PEER_ID}(${POINTER_AGENT})",
  stream_opened_at: "${TIMESTAMP}: Bitswap connected to peer ${PROVIDER_PEER_ID}",
  received_first_HAVE_at: "${TIMESTAMP}: Got provider ${PROVIDER_PEER_ID} for content ${CID}",
  done_retrieving_at: "${TIME_STAMP}: Done retrieving content for ${CID} error: ${ERROR_MESSAGE:''}",
  finished_searching_providers_at: "${TIME_STAMP}: Finish searching providers for cid ${CID} with ctx error: ${ERROR_MESSAGE:''}"
}
```

## Regex -> Template Log Mapping

```
{
  ([^\s]+): Start retrieving content for ([^\s]+) :
  ${TIMESTAMP}: Start retrieving content for ${CID},

  ([^\s]+): Start searching providers for cid (\w+) :
  ${TIMESTAMP}: Start searching providers for cid ${CID},

  ([^\s]+): Found provider (\w+) for cid ([^\s]+) from (\w+)\((.+)\) :
  ${TIMESTAMP}: Found provider ${PROVIDER_PEER_ID} for cid ${CID} from ${POINTER_PEER_ID}(${POINTER_AGENT}),

  ([^\s]+): Bitswap connect to peer (\w+):
  ${TIMESTAMP}: Bitswap connect to peer ${PROVIDER_PEER_ID},

  ([^\s]+): Connected to provider (\w+)\((.+)\) for cid ([^\s]+) from (\w+)\((.+)\):
  ${TIMESTAMP}: Connected to provider ${PROVIDER_PEER_ID}(${PROVIDER_AGENT}) for cid ${CID} from ${POINTER_PEER_ID}(${POINTER_AGENT}),

  ([^\s]+): Bitswap connected to peer (\w+):
  ${TIMESTAMP}: Bitswap connected to peer ${PROVIDER_PEER_ID},

  ([^\s]+): Got provider (\w+) for content (\w+):
  ${TIMESTAMP}: Got provider ${PROVIDER_PEER_ID} for content ${CID},

  ([^\s]+): Done retrieving content for (\w+) error: (.+)?:
  ${TIME_STAMP}: Done retrieving content for ${CID} error: ${ERROR_MESSAGE:''},

  ([^\s]+): Finish searching providers for cid (\w+) with ctx error: (.+)?:
  ${TIME_STAMP}: Finish searching providers for cid ${CID} with ctx error: ${ERROR_MESSAGE:''},
}
```
