# Jules REST API v1alpha — Quick Reference

Base URL: `https://jules.googleapis.com/v1alpha`
Auth header: `x-goog-api-key: $JULES_API_KEY`

## Sources

```
GET  /v1alpha/sources              → list [?pageSize=&pageToken=&filter=]
GET  /v1alpha/{name=sources/**}    → get <name>
```

Source name format: `sources/github/{owner}/{repo}`

## Sessions

```
GET    /v1alpha/sessions                                → list
GET    /v1alpha/{name=sessions/*}                       → get
POST   /v1alpha/sessions                                → create (body = Session)
POST   /v1alpha/{session=sessions/*}:sendMessage        → send message
POST   /v1alpha/{session=sessions/*}:approvePlan        → approve plan
DELETE /v1alpha/{name=sessions/*}                       → delete (unofficial)
POST   /v1alpha/{session=sessions/*}:cancel             → cancel (unofficial)
POST   /v1alpha/{session=sessions/*}:pause              → pause (unofficial)
POST   /v1alpha/{session=sessions/*}:resume             → resume (unofficial)
```

### Session States
`QUEUED` → `PLANNING` → `IN_PROGRESS` / `AWAITING_PLAN_APPROVAL` / `AWAITING_USER_FEEDBACK` → `COMPLETED` / `FAILED` / `PAUSED`

### AutomationMode
- `AUTOMATION_MODE_UNSPECIFIED` — no automation (default)
- `AUTO_CREATE_PR` — auto branch + PR ✅

## Activities

```
GET /v1alpha/{parent=sessions/*}/activities             → list [?pageSize=&pageToken=&createTime=ISO8601]
GET /v1alpha/{name=sessions/*/activities/*}             → get
```

### Activity Types (union field)
| Type | Key Field |
|------|-----------|
| `agentMessaged` | `.agentMessage` |
| `userMessaged` | `.userMessage` |
| `planGenerated` | `.plan.steps[]` |
| `planApproved` | `.planId` |
| `progressUpdated` | `.title`, `.description` |
| `sessionCompleted` | (empty) |
| `sessionFailed` | `.reason` |

### Artifact Types
- `changeSet` → `.gitPatch.unidiffPatch`
- `media` → `.data` (base64), `.mimeType`
- `bashOutput` → `.command`, `.output`, `.exitCode`

## Usage Limits

| Plan  | Daily (24h) | Concurrent |
|-------|-------------|------------|
| Free  | 15          | 3          |
| Pro   | 100         | 15         |
| Ultra | 300         | 60         |

## References

- [API Overview](https://jules.google/docs/api/reference/overview)
- [Sessions](https://jules.google/docs/api/reference/sessions)
- [Activities](https://jules.google/docs/api/reference/activities)
- [Types](https://jules.google/docs/api/reference/types)
- [Usage Limits](https://jules.google/docs/usage-limits/)
