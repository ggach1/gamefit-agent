const button = document.querySelector('#analyze');
const result = document.querySelector('#result');
const errorBox = document.querySelector('#error');

const chips = (items, kind) => items.length
  ? `<div class="chips">${items.map(x => `<span class="chip ${kind}">${escapeHtml(x)}</span>`).join('')}</div>`
  : '<span class="metric">없음</span>';

const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
}[char]));

button.addEventListener('click', async () => {
  errorBox.textContent = '';
  button.disabled = true;
  button.firstChild.textContent = '분석 중... ';
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        job_posting: document.querySelector('#job').value,
        candidate_profile: document.querySelector('#profile').value
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '분석에 실패했습니다.');
    result.innerHTML = `
      <div class="card-title"><span>02</span><div><b>분석 결과</b><small>에이전트가 4개 도구를 순차 실행했습니다.</small></div></div>
      <div class="score-row"><div class="score">${data.fit.score}<small>점</small></div><div class="metric"><b>적합도 ${data.fit.level}</b>핵심 기술 ${data.fit.matched_skills.length}개 일치</div><span class="badge">분석 완료</span></div>
      <h3>일치하는 기술</h3>${chips(data.fit.matched_skills, 'ok')}
      <h3>보완이 필요한 기술</h3>${chips(data.fit.missing_skills, 'miss')}
      <h3>에이전트 실행 과정</h3><ol class="steps">${data.trace.map(step => `<li><b>${escapeHtml(step.tool)}</b> · ${escapeHtml(step.reason)}</li>`).join('')}</ol>
      <h3>추천 개선 계획</h3><ul class="plan">${data.improvement_plan.actions.map(action => `<li>${escapeHtml(action)}</li>`).join('')}</ul>`;
  } catch (error) {
    errorBox.textContent = error.message;
  } finally {
    button.disabled = false;
    button.firstChild.textContent = '에이전트 분석 시작 ';
  }
});

// 문서용 실행 화면을 재현할 때만 샘플 분석을 자동 실행한다.
if (new URLSearchParams(window.location.search).get('demo') === '1') {
  button.click();
}
