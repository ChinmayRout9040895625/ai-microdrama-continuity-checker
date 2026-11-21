"""Data shapes. The *Out models are what the LLM must return (structured output);
the rest are what our code builds around them."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

Category = Literal[
    "identity",      # name, alias, true identity, nationality
    "age",
    "occupation",    # job, company, title
    "relationship",  # family ties, marriage, romance, employer, friendship
    "status",        # alive/dead, injured, pregnant, in prison, missing...
    "knowledge",     # who knows which secret
    "location",      # where someone lives / is
    "possession",    # objects, money, property
    "timeline",      # when/order of past events, durations
    "other",
]


# ---------- LLM output: extraction ----------
class CharacterOut(BaseModel):
    name: str = Field(description="Most complete name used for the character in this episode")
    aliases: list[str] = Field(description="Other names/titles used for the same person in this episode, e.g. 'Mr. Grant', 'Alex', 'Mom'")


class FactOut(BaseModel):
    entity: str = Field(description="Character (or place/company) the fact is about, using a name from `characters` when possible")
    category: Category
    target: Optional[str] = Field(description="Other character/thing the fact relates to (e.g. for relationship: the other person; for knowledge: the secret's subject). null if none")
    value: str = Field(description="The fact itself, short and specific, e.g. 'mother is dead', 'is 28 years old', 'knows Lily is the CEO's daughter'")
    quote: str = Field(description="VERBATIM excerpt (5-30 words) copied exactly from the episode text that establishes this fact")


class EpisodeFactsOut(BaseModel):
    characters: list[CharacterOut]
    facts: list[FactOut]


# ---------- LLM output: continuity check ----------
class IssueOut(BaseModel):
    # Field order matters: the model writes the reasoning BEFORE committing to a verdict.
    prior_fact_id: str = Field(description="ID of the earlier fact, e.g. 'E03-F07'")
    new_fact_id: str = Field(description="ID of the fact in the current episode that conflicts with it, e.g. 'E09-F02'")
    explanation: str = Field(description="One or two sentences: why these cannot both be true")
    is_real_contradiction: bool = Field(description="After writing the explanation: are these two facts truly incompatible? False if, on reflection, they can both be true")
    issue_type: Category
    severity: Literal["high", "medium", "low"] = Field(description="high = a hard fact a viewer would clearly notice (name, age, death, family tie, amount); medium = noticeable on close watching; low = minor wording/timing detail")
    could_be_intentional: bool = Field(description="True if this could be a deliberate twist/lie/reveal rather than a mistake")
    suggested_fix: str = Field(description="Smallest script edit that would resolve it")


class CheckOut(BaseModel):
    issues: list[IssueOut]


# ---------- Internal ----------
class Episode(BaseModel):
    number: int
    title: str
    text: str


class Fact(BaseModel):
    id: str
    episode: int
    entity: str
    entity_key: str = ""   # canonical entity after alias merging
    category: Category
    target: Optional[str] = None
    value: str
    quote: str
    quote_score: float = 0.0  # fuzzy match of quote against source text (0-100)


class Issue(BaseModel):
    id: str
    prior: Fact
    new: Fact
    issue_type: Category
    severity: Literal["high", "medium", "low"]
    explanation: str
    could_be_intentional: bool
    suggested_fix: str
