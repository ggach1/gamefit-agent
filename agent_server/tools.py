"""에이전트가 호출할 도구와 등록소.

도구 함수는 ``@tool`` 데코레이터로 등록된다. 에이전트는 함수 이름을
하드코딩해 직접 호출하지 않고 REGISTRY를 통해 실행한다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    function: Callable[..., dict[str, Any]]


REGISTRY: dict[str, ToolSpec] = {}


def tool(name: str, description: str) -> Callable:
    """함수를 에이전트 도구로 등록하는 데코레이터."""

    def decorator(function: Callable[..., dict[str, Any]]) -> Callable:
        REGISTRY[name] = ToolSpec(name, description, function)
        return function

    return decorator


SKILLS = {
    "언어": ["c++", "c#", "python", "java", "javascript", "typescript", "lua", "go"],
    "엔진": ["unity", "unreal", "언리얼", "유니티", "godot"],
    "서버": ["tcp", "udp", "http", "rest", "websocket", "socket", "grpc", "network"],
    "데이터": ["mysql", "postgresql", "redis", "mongodb", "sql", "database", "db"],
    "협업": ["git", "jira", "notion", "agile", "협업", "커뮤니케이션"],
    "운영": ["aws", "docker", "kubernetes", "linux", "ci/cd", "jenkins", "cloud"],
}

DISPLAY_NAMES = {
    "tcp": "TCP", "udp": "UDP", "http": "HTTP", "rest": "REST",
    "grpc": "gRPC", "mysql": "MySQL", "postgresql": "PostgreSQL",
    "redis": "Redis", "mongodb": "MongoDB", "sql": "SQL", "db": "DB",
    "git": "Git", "github": "GitHub", "jira": "Jira", "aws": "AWS",
    "docker": "Docker", "kubernetes": "Kubernetes", "linux": "Linux",
    "python": "Python", "java": "Java", "javascript": "JavaScript",
    "typescript": "TypeScript", "unity": "Unity", "unreal": "Unreal",
    "godot": "Godot", "c++": "C++", "c#": "C#", "ci/cd": "CI/CD",
}


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _extract_skills(text: str) -> list[dict[str, str]]:
    normalised = _normalise(text)
    found: list[dict[str, str]] = []
    for category, names in SKILLS.items():
        for skill in names:
            # 짧은 토큰(go, db 등)은 단어 경계를 확인해 오탐을 줄인다.
            # GitHub는 Git 경험으로도 인정한다.
            token = "git(?:hub)?" if skill == "git" else re.escape(skill)
            pattern = rf"(?<![a-z0-9]){token}(?![a-z0-9])"
            if re.search(pattern, normalised):
                display = DISPLAY_NAMES.get(skill, skill.title())
                found.append({"name": display, "category": category})
    return found


@tool("extract_requirements", "채용공고에서 기술 스택과 주요 요구사항을 추출합니다.")
def extract_requirements(job_posting: str) -> dict[str, Any]:
    skills = _extract_skills(job_posting)
    preferred_markers = ("우대", "preferred", "plus", "경험자")
    sentences = [s.strip() for s in re.split(r"[\n.!?]+", job_posting) if s.strip()]
    preferred = [s for s in sentences if any(marker in s.lower() for marker in preferred_markers)]
    required = [s for s in sentences if s not in preferred]
    return {
        "skills": skills,
        "required_points": required[:6],
        "preferred_points": preferred[:4],
    }


@tool("extract_candidate_skills", "지원자 소개에서 보유 기술과 경험을 추출합니다.")
def extract_candidate_skills(candidate_profile: str) -> dict[str, Any]:
    return {
        "skills": _extract_skills(candidate_profile),
        "profile_length": len(candidate_profile.strip()),
    }


@tool("calculate_fit", "공고 요구 기술과 지원자 기술을 비교해 적합도를 계산합니다.")
def calculate_fit(requirements: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    required = {item["name"] for item in requirements["skills"]}
    owned = {item["name"] for item in candidate["skills"]}
    matched = sorted(required & owned)
    missing = sorted(required - owned)
    extra = sorted(owned - required)
    score = round(len(matched) / len(required) * 100) if required else 0
    level = "높음" if score >= 75 else "보통" if score >= 45 else "낮음"
    return {
        "score": score,
        "level": level,
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
    }


@tool("generate_improvement_plan", "부족한 역량을 바탕으로 우선순위별 개선 계획을 만듭니다.")
def generate_improvement_plan(missing_skills: list[str]) -> dict[str, Any]:
    if not missing_skills:
        return {"summary": "핵심 기술 요구사항을 모두 충족합니다.", "actions": [
            "프로젝트 성과를 수치로 정리해 포트폴리오에 추가하세요.",
            "면접에서 설명할 기술 의사결정 사례를 준비하세요.",
        ]}
    actions = [
        f"{skill}: 공식 문서 학습 후 작은 데모를 제작해 GitHub에 공개"
        for skill in missing_skills[:3]
    ]
    actions.append("완성한 데모의 문제 상황, 해결 과정, 결과를 README에 기록")
    return {
        "summary": f"우선 보완할 기술은 {', '.join(missing_skills[:3])}입니다.",
        "actions": actions,
    }
