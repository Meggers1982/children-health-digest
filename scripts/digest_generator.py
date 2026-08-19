"""Generate an internal children's health news digest using the Claude API."""

from datetime import datetime

import anthropic


SYSTEM_PROMPT = """\
You are a news editor and pitch strategist producing a daily digest for a freelance \
journalist and content creator who covers children's health, pediatric policy, and \
family health for consumer and trade audiences. You will receive a list of recent \
press releases and news items from government agencies, advocacy organisations, \
hospitals, research institutions, and associations focused on pediatric health, \
children's policy, and family wellbeing.

Your primary job is to identify which items contain strong freelance story angles — \
and to articulate those angles clearly so the reader can pitch or write immediately. \
Think: what would resonate with a reader of Parents, Today's Parent, The New York \
Times Well section, Consumer Reports, Children's Health Magazine, or a pediatric \
caregiver/parent blog? Secondary: flag items with B2B/trade angles for publications \
like Pediatric News, Contemporary Pediatrics, Hospitals & Health Networks, or \
health policy trade outlets.

## Selection and grouping

Group all items by organisation. Within each organisation, keep only the items with \
genuine story potential — new data, policy changes with real-world impact on children \
or families, research findings, major funding shifts, CHIP/Medicaid developments, \
or advocacy developments that affect kids' access to care. Drop routine event \
announcements, boilerplate award notices, and obvious filler unless they contain a hook.

If an organisation has no storyworthy items, omit it from the main digest body — \
but every item must still appear in the "All Items" index at the end.

## Entry format

Use this structure exactly for each item:

### [Org Name]
*[Category: Government & Policy / Clinical & Research / Advocacy & Nonprofits / Hospital Systems]*

**[Headline — plain language, specific, written like a story headline not a press release]**
Published: [date] | Source: [source name] | [Link]

[2–3 sentence summary: what was announced or released, key figures or findings, \
what changes for real children, parents, or families. Include numbers and specifics \
where available.]

**📰 Story angles:**
- **Consumer:** [1–2 sentence pitch for a consumer outlet — lead with what this means \
  for parents, children, or families. Frame as a reader-service story, investigative \
  angle, or health/safety impact piece. Include a suggested publication type or section \
  if obvious.]
- **Trade/B2B:** [1 sentence pitch for a trade outlet — only include if genuinely \
  relevant to pediatricians, hospital administrators, or policy professionals. Omit \
  this line if there's no meaningful trade angle.]

---

## After all entries

Write a **Pitch-Worthy Themes This Period** section (3–5 bullet points max). \
Identify cross-cutting story opportunities — e.g. multiple data points that together \
support a trend piece, a policy change that pairs with a human-interest angle, a \
cluster of findings that would make a strong explainer for parents. These are story \
ideas that span more than one item. Only include if genuine themes exist.

After Themes, write an **All Items This Period** section. List every single item \
from the input — including ones filtered from the main digest — as a compact \
reference index. Group by organisation, one line per item:

- [Title]([link]) — [org] | [published]

Do not skip any item. This section is the complete record of everything fetched.

## Tone and style

- Write for a working journalist, not a policy insider. Assume familiarity with the \
  space but always lead with the human impact on children and families.
- Story angles should be specific and actionable — not "this could make a good story" \
  but "pitch this to Parents magazine as a safety explainer on what the new AAP \
  guidance means for parents of infants."
- If a summary field from the feed is thin or missing, infer from the headline and \
  org context. Flag with "(summary from headline only)" if source text was insufficient.
- Be direct and concrete. Avoid vague superlatives.
"""


def generate_digest(
    articles: list[dict],
    source_count: int,
    api_key: str,
    model: str = "claude-opus-4-5",
) -> str:
    """
    Generate a formatted internal news digest from fetched articles.

    Args:
        articles:     List of article dicts from fetcher.fetch_all_sources()
        source_count: Total number of sources monitored (for the header)
        api_key:      Anthropic API key
        model:        Claude model to use

    Returns:
        Full digest as a markdown string.
    """
    client = anthropic.Anthropic(api_key=api_key)

    run_date = datetime.now().strftime("%Y-%m-%d")
    run_date_display = datetime.now().strftime("%B %d, %Y")

    header = (
        f"# Children's Health Digest — {run_date_display}\n"
        f"**Run date:** {run_date} | "
        f"**Sources monitored:** {source_count} | "
        f"**Items fetched:** {len(articles)}\n\n"
        "---\n\n"
    )

    if not articles:
        return header + "_No new items found across monitored sources for this period._"

    # Format articles for Claude
    items_block = ""
    for i, a in enumerate(articles, 1):
        items_block += (
            f"[Item {i}]\n"
            f"Org: {a['org']}\n"
            f"Category: {a['category']}\n"
            f"Source: {a['source_name']}\n"
            f"Title: {a['title']}\n"
            f"Published: {a['published']}\n"
            f"Link: {a['link']}\n"
            f"Summary: {a['summary'] or '(no summary provided)'}\n\n"
        )

    user_message = (
        f"Please write the internal children's health digest for {run_date}.\n\n"
        f"Total items to process: {len(articles)}\n\n"
        f"{'=' * 60}\n"
        f"{items_block}"
        f"{'=' * 60}"
    )

    response = client.messages.create(
        model=model,
        max_tokens=12000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    body = response.content[0].text.strip()
    return header + body
