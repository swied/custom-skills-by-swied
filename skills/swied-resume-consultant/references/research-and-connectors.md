# Research and Connector Guide

Read this guide before accessing a profile connector, researching openings, or
advising the user about MCP installation.

## Contents

- [Privacy-first research](#privacy-first-research)
- [LinkedIn-capable connector protocol](#linkedin-capable-connector-protocol)
- [Installation guidance](#installation-guidance-when-the-connector-is-missing)
- [Job-market research loop](#job-market-research-loop)
- [Company and compensation research](#company-and-compensation-research)
- [Source discipline](#source-discipline)

## Privacy-first research

- Use public, de-identified searches by default: role, level, industry, skill,
  location, and work arrangement.
- Obtain permission before searching the user's name, profile URL, or other
  identifying details.
- Do not submit confidential employer data, unpublished metrics, private client
  names, or personal contact details to search engines.
- Ask before sending resume content to a third-party connector. Use only the
  minimum data and read-only scope needed for intake.
- Never request a password, session cookie, access token, or API secret in chat.

## LinkedIn-capable connector protocol

First inspect the tools actually exposed in the current session. A generic web
browser is not a LinkedIn profile connector. Do not pretend that a public profile
URL guarantees access to the full profile.

If an authorized connector is available:

1. Identify what data it can read and whether it can also write.
2. Explain the intended read-only use and ask the user for permission.
3. Request the minimum available scope and access only the user's own profile.
4. Attribute imported information to the connector and ask the user to confirm it.
5. Do not edit, post, message, apply, or access other members' data.

If no connector is available, say plainly:

> I don't see a LinkedIn-capable connector in this session. We can continue now
> with a resume, a LinkedIn export or pasted profile text, or your career story.
> If you want a connector, I can help you verify and install one for your specific
> AI harness.

Then continue the interview. Do not make installation a prerequisite.

## Installation guidance when the connector is missing

There is no universal "LinkedIn MCP" installation command. Server availability,
authorization, and client configuration change over time. Give exact steps only
after completing this protocol:

1. Determine the user's harness, version, operating system, and whether it
   supports local stdio or remote HTTP MCP servers.
2. Consult the harness's current official MCP documentation.
3. Search for a candidate server. Prefer a LinkedIn-published, harness-managed,
   or organization-approved integration. Do not imply that a community server is
   official or endorsed.
4. Verify the package or repository owner, release history, source code,
   transport, requested LinkedIn scopes, credential storage, data retention,
   privacy policy, and uninstall instructions. Check the current LinkedIn terms
   and API access rules. Reject servers that scrape pages, reuse browser cookies,
   automate account activity, or request unexplained broad permissions.
5. If no trustworthy, authorized connector can be verified, say so and recommend
   a user-controlled export or pasted resume instead.
6. Before any change, show the user the source URL, exact command or config diff,
   requested scopes, authentication flow, restart step, verification step, and
   rollback procedure. Obtain explicit approval before installing software,
   editing configuration, or authenticating.
7. Store secrets only through the harness or operating system's supported secret
   mechanism, never in the career Markdown files or chat.
8. Restart or reload the harness as its current documentation requires, list the
   newly exposed tools, and make one read-only verification call with consent.

If the harness cannot be identified, ask for its name rather than guessing its
configuration format. Research current official documentation at runtime instead
of relying on remembered commands.

LinkedIn's official API documentation says member-data access is authenticated,
permissioned, and restricted, while its user agreement prohibits unauthorized
scraping and automated access. Recheck these sources at runtime because terms and
permissions change:

- [Getting Access to LinkedIn APIs](https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access)
- [LinkedIn Profile API](https://learn.microsoft.com/en-us/linkedin/shared/integrations/people/profile-api)
- [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement)
- [LinkedIn prohibited software and extensions](https://www.linkedin.com/help/linkedin/answer/a1341387)
- [MCP security best practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)

## Job-market research loop

### Define each query

Combine the current hypothesis with:

- two or three plausible titles and truthful synonyms;
- seniority and scope;
- industry or problem domain;
- location, remote or hybrid preference, and work authorization when relevant;
- must-have constraints; and
- current date or freshness filters where the search tool supports them.

Do not include the user's name or confidential resume facts unless the user
explicitly asks for a public-background search.

### Build a representative posting set

Start with roughly six to twelve active postings across the leading hypotheses.
Favor employer career pages. Use reputable job boards for discovery, then verify
the opening at its original source when possible. Include some variation in
company size or industry so one employer's vocabulary does not define the market.

For each posting, capture in the profile or report:

- title, employer, location and work arrangement;
- level and compensation when stated;
- URL and access date;
- evidence that the posting is active;
- core responsibilities and outcomes;
- required versus preferred skills, tools, domain experience, and credentials;
- recurring phrases worth using only when truthful; and
- fit evidence, uncertainty, and gaps for this user.

Treat an absent salary or ambiguous requirement as unknown. Do not infer that an
old aggregator page represents an active opening.

### Synthesize without overfitting

Count concepts as well as exact words. Group honest variants such as "cross-
functional leadership" and "matrix leadership," but preserve the wording that
is common in target postings. Separate:

- common requirements across the sample;
- role-family signals that distinguish one hypothesis from another;
- employer-specific preferences; and
- requirements that may be negotiable based on equivalent evidence.

Bring only the highest-impact gaps back into the interview. A missing keyword is
not a missing skill until the user has been asked for evidence.

## Company and compensation research

Recommend companies only when an active role, credible hiring signal, or clear
strategic fit supports the suggestion. Explain why each company fits the user's
criteria and note risks or unknowns. Do not present employer branding as fact
about the lived employee experience.

For compensation:

1. Establish geography, level, function, industry, company stage or size, work
   arrangement, and whether the user means base pay or total compensation.
2. Prefer current posted ranges and government or other authoritative datasets;
   triangulate with a second credible source when possible.
3. Normalize currency and time period. Separate base, bonus, commission, equity,
   benefits, and total compensation.
4. Present a reasoned range, not false precision. State the access date, sample
   limitations, and assumptions.
5. Distinguish the user's floor, target, and stretch outcome from the market range.

## Source discipline

For every time-sensitive recommendation, keep a source log with a descriptive
title, direct URL, access date, and the claim it supports. Link to original
postings and primary or authoritative sources whenever possible. Clearly label
Dr. Bailey's synthesis as an inference. Do not copy long passages from job postings;
extract short phrases and summarize the rest.
