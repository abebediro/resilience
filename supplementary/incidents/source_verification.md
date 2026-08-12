# Data Collection and Source Verification Protocol

## Search strategy and database coverage

| Database | Search terms | Results | Included | Rate |
|---|---|---|---|---|
| IEEE Xplore | "satellite cyber" OR "space cybersecurity" OR "SATCOM attack" | 247 | 18 | 7.3% |
| ACM Digital Library | "satellite security" OR "space system attack" | 156 | 12 | 7.7% |
| Scopus | "space system" AND "cyber attack" OR "satellite compromise" | 389 | 24 | 6.2% |
| Space-ISAC | Incident reports (2007–2022) | 45 | 31 | 68.9% |
| Government Repositories | NASA OIG, CISA, ESA reports, GAO | 67 | 19 | 28.4% |
| News (vetted) | Reuters, AP, SpaceNews, BBC, Der Spiegel | 412 | 28 | 6.8% |
| Academic Journals | Journal of Space Safety Engineering, etc. | 89 | 12 | 13.5% |
| Conference Proceedings | SmallSat, AIAA, IAC | 112 | 8 | 7.1% |
| Industry Reports | Vendor disclosures, threat intelligence | 78 | 14 | 17.9% |
| **Total (raw hits)** | | **1595** | | |

After removing duplicates, 1,316 unique records were screened, 166
full-text reviewed, and 70 incidents included. Per-database inclusion
counts overlap across multi-source incidents.

## Inclusion / exclusion criteria

| Criterion | Include | Exclude | Rationale |
|---|---|---|---|
| Time period | 2007–2022 | Pre-2007 | Modern threat landscape post-2007 |
| Documentation | >= 2 independent sources | Single source only | Verification reliability |
| Codability | Codable on all five dimensions | Insufficient detail | Must code all dimensions |
| System type | Space or supporting ground segment | General IT only | Space-specific focus |
| Attribution | Not required | — | Not needed for impact analysis |
| Language | English | Non-English | Translation resources limited |
| Availability | Public or member-accessible | Classified beyond summaries | Transparency |

## Source verification matrix

| Source type | Minimum requirement | Verification method | Confidence | # used |
|---|---|---|---|---|
| Government reports | Official document with reference number | Cross-reference with agency database | High | 19 |
| Academic papers | Peer-reviewed, methodology described | Independent replication possible | High | 12 |
| Space-ISAC advisories | Advisory number, member verification | Industry confirmation | Med-High | 31 |
| News media | Two independent outlets | Cross-source corroboration | Medium | 28 |
| Vendor disclosures | Official statement | Public-record verification | Medium | 14 |
| Conference proceedings | Published in proceedings | Peer-review confirmation | Medium | 8 |

## Source quality distribution

| Score | Criteria | Count | % |
|---|---|---|---|
| 5 | Multiple independent primary sources; official reports; full technical detail | 12 | 17.1% |
| 4 | Two independent sources; official disclosures; most detail | 28 | 40.0% |
| 3 | Single official source plus media; partial detail | 22 | 31.4% |
| 2 | Single source; media only; limited detail | 8 | 11.4% |
| 1 | Unconfirmed; single media source; minimal detail | 0 | 0.0% |
