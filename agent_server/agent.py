"""도구 선택 및 실행을 담당하는 에이전트 오케스트레이터."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .tools import REGISTRY


class GameJobAgent:
    """입력 상태를 판단해 필요한 도구를 순서대로 선택하고 실행한다."""

    def list_tools(self) -> list[dict[str, str]]:
        return [
            {"name": spec.name, "description": spec.description}
            for spec in REGISTRY.values()
        ]

    def select_tools(self, job_posting: str, candidate_profile: str) -> list[str]:
        """단순하지만 설명 가능한 규칙 기반 도구 선택 로직."""
        selected: list[str] = []
        if job_posting.strip():
            selected.append("extract_requirements")
        if candidate_profile.strip():
            selected.append("extract_candidate_skills")
        if len(selected) == 2:
            selected.extend(["calculate_fit", "generate_improvement_plan"])
        return selected

    def _invoke(self, name: str, **kwargs: Any) -> dict[str, Any]:
        spec = REGISTRY.get(name)
        if spec is None:
            raise ValueError(f"등록되지 않은 도구입니다: {name}")
        return spec.function(**kwargs)

    def analyze(self, job_posting: str, candidate_profile: str) -> dict[str, Any]:
        if not job_posting.strip() or not candidate_profile.strip():
            raise ValueError("채용공고와 지원자 소개를 모두 입력해 주세요.")

        selected = self.select_tools(job_posting, candidate_profile)
        trace: list[dict[str, Any]] = []

        requirements = self._invoke("extract_requirements", job_posting=job_posting)
        trace.append({"tool": "extract_requirements", "reason": "채용공고가 입력되어 요구 기술 추출이 필요함"})

        candidate = self._invoke("extract_candidate_skills", candidate_profile=candidate_profile)
        trace.append({"tool": "extract_candidate_skills", "reason": "지원자 보유 기술을 비교 가능한 형태로 변환"})

        fit = self._invoke("calculate_fit", requirements=requirements, candidate=candidate)
        trace.append({"tool": "calculate_fit", "reason": "공고 기술과 지원자 기술이 모두 준비되어 적합도 계산 가능"})

        plan = self._invoke("generate_improvement_plan", missing_skills=fit["missing_skills"])
        trace.append({"tool": "generate_improvement_plan", "reason": "분석된 부족 역량을 실행 계획으로 변환"})

        return {
            "agent": "GameFit Agent",
            "selected_tools": selected,
            "trace": trace,
            "requirements": requirements,
            "candidate": candidate,
            "fit": fit,
            "improvement_plan": plan,
            "disclaimer": "키워드 기반 참고 분석이며 실제 채용 결과를 보장하지 않습니다.",
        }

