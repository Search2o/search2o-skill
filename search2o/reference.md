# Search2o reference

Both calls are POST, under `/api/exec`, with `Authorization: Bearer <token>`.

## search

Request: `{"query": "...", "tag": "..."}`. The query is 8 to 1000 characters. `tag` is
optional and filters to agents carrying that tag.

Response:

| field | meaning |
|---|---|
| `searchResults` | the matching agents, best first, each `{agentName, agentTitle}` |

There are no descriptions in a result. Choose on `agentTitle`.

The response also carries `searchBehavior` and `followupBehavior`. Those tell a user
interface what to do when it cannot judge for itself. Ignore them and pick the agent that
fits the request.

## execAgent

Request: `{"agentName": "...", "convid": "...", "inputs": {...}, "stream": false}`.
`agentName` is required. Omit `convid` to start a conversation, and send it back to
continue one. Put the person's request in `inputs` under `query`; an agent may take other
inputs too. Leave `stream` false: this script reads one JSON object.

A conversation is not tied to one agent. Any agent can run in it, and each sees the earlier
turns, so several requests can share one conversation. The exception is a conversation
waiting on an `ask`: until that agent has its answers, every other agent gets
`unknownConversation`, with the message "This conversation is waiting for your answers to
another agent. Continue it with that agent."

Response: `{convid, agentName, output, resultCode, askInput}`.

`output` is `{agentName, parts}`. Each part has a `contentType`:

| contentType | fields | what to do |
|---|---|---|
| `text` | `text` | show it as it is |
| `html` | `text` | do not render it; summarize, and link to the conversation in the GUI |
| `image` | `text` (base64), `mimeType` | describe it; it is not a URL |

## Result codes

| resultCode | meaning | what to do |
|---|---|---|
| `success` | the agent finished | show the output |
| `ask` | the agent needs answers | ask the questions in `askInput`, then call again with the same `convid` and the answers in `inputs` |
| `failCommand` | the agent stopped itself | show the message in `error.message`; it was written for the person |
| `errorInAgent` | the agent has a fault | say the agent failed and report it to whoever owns the agent |
| `callFailed` | a system the agent called failed, or the agent does not exist | say so; worth retrying once |
| `unknownConversation` | the conversation expired, or it is paused on a different agent | start a new conversation without `convid` |
| `timedOut` | the agent ran past the account's time limit | say so; do not retry automatically |
| `stopped` | someone cancelled the run | say so |
| `mustLogin` | the token expired mid-run | ask the person for a new token |
| `unexpected` | an unhandled fault | say the agent failed and report it |

## askInput

`{"message": "...", "inputs": [{"name", "type", "label", "description", "options", "default", "hidden"}]}`.

`type` is `str`, `password`, `text`, `chooseOne` or `chooseMany`. `options` lists the
choices for the two choose types. A `hidden` input is not for the person: send its
`default` back unchanged. Never ask for a `password` input in chat.

## Errors

A failed call is not 200. The body is `{"success": false, "error": {"message": "..."}}`,
and the script turns it into a message on stderr with a non-zero exit. 401 means the token
was refused, and 403 means the token may not do that.
