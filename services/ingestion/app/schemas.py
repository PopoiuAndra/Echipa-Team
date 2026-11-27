from __future__ import annotations

from pydantic import BaseModel, Field


class WeightedSkill(BaseModel):
    uri: str
    proficiency: float = Field(ge=0.0, le=1.0)


class WeightedPreference(BaseModel):
    uri: str
    weight: float = Field(ge=0.0, le=1.0)


class WeightedAversion(BaseModel):
    uri: str
    severity: float = Field(gt=0.0, le=1.0)


class GithubIngestRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    github_username: str = Field(min_length=1, max_length=100)
    extra_preferences: list[str] = Field(default_factory=list)
    extra_aversions: list[str] = Field(default_factory=list)


class ProfileIngestRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    location_qid: str | None = None
    education: str | None = None
    occupation: str | None = None
    driving_license: bool = False
    skills: list[WeightedSkill] = Field(default_factory=list)
    preferences: list[WeightedPreference] = Field(default_factory=list)
    aversions: list[WeightedAversion] = Field(default_factory=list)


class IngestResponse(BaseModel):
    user_uri: str
    triples_inserted: int
    extracted_skills: list[str] = Field(default_factory=list)
    status: str = "ok"
