const button = document.querySelector('#analyze');
const result = document.querySelector('#result');
const errorBox = document.querySelector('#error');
const mode = document.querySelector('#source-mode');
const filesInput = document.querySelector('#job-images');
function updateMode() {
  for (const name of ['url','images','text']) document.querySelector(`#${name}-panel`).hidden = mode.value !== name;
}
mode.addEventListener('change', updateMode);
filesInput.addEventListener('change', () => {
  const list = document.querySelector('#image-list');
  list.replaceChildren();
  for (const file of filesInput.files) {
    const item = document.createElement('li');
    item.textContent = `${file.name} (${(file.size / 1000000).toFixed(1)} MB)`;
    list.append(item);
  }
});
function readImage(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve({data: String(reader.result).split(',')[1]});
    reader.onerror = () => reject(new Error('이미지 파일을 읽지 못했습니다.'));
    reader.readAsDataURL(file);
  });
}

const chips = (items, kind) => items.length
  ? `<div class="chips">${items.map(x => `<span class="chip ${kind}">${escapeHtml(x)}</span>`).join('')}</div>`
  : '<span class="metric">없음</span>';

const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
}[char]));

button.addEventListener('click', async () => {
  errorBox.textContent = '';
  result.innerHTML = '<p role="status">공고 분석 중… 이미지 공고는 로컬 OCR로 처리하며 잠시 시간이 걸릴 수 있습니다.</p>';
  button.disabled = true;
  button.firstChild.textContent = '분석 중... ';
  try {
    const payload = {candidate_profile: document.querySelector('#profile').value};
    if (!payload.candidate_profile.trim()) throw new Error('나의 기술·경험을 입력하세요.');
    if (mode.value === 'images') {
      const files = Array.from(filesInput.files);
      if (!files.length || files.length > 6) throw new Error('이미지를 1~6장 선택하세요.');
      if (files.some(file => !file.size || file.size > 12000000) || files.reduce((s,f) => s + f.size, 0) > 24000000) throw new Error('이미지는 장당 12MB, 전체 24MB 이하여야 합니다.');
      payload.images = await Promise.all(files.map(readImage));
    } else if (mode.value === 'url') {
      payload.job_url = document.querySelector('#job-url').value.trim();
      if (!payload.job_url) throw new Error('공고 링크를 입력하거나 다른 입력 방법을 선택하세요.');
    } else payload.job_posting = document.querySelector('#job').value;
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '분석에 실패했습니다.');
    result.innerHTML = `
      <div class="card-title"><span>02</span><div><b>분석 결과</b><small>에이전트가 4개 도구를 순차 실행했습니다.</small></div></div>
      <div class="score-row"><div class="score">${data.fit.score}<small>점</small></div><div class="metric"><b>기술 일치율 · ${data.fit.level}</b>인식된 기술 ${data.fit.matched_skills.length}개 일치</div><span class="badge">분석 완료</span></div>
      <p class="metric">기술 사전과 추출된 텍스트 기준입니다. 합격 확률이나 모든 자격요건 충족을 의미하지 않습니다.</p>
      <h3>일치하는 기술</h3>${chips(data.fit.matched_skills, 'ok')}
      <h3>보완이 필요한 기술</h3>${chips(data.fit.missing_skills, 'miss')}
      <h3>에이전트 실행 과정</h3><ol class="steps">${data.trace.map(step => `<li><b>${escapeHtml(step.tool)}</b> · ${escapeHtml(step.reason)}</li>`).join('')}</ol>
      <h3>추천 개선 계획</h3><ul class="plan">${data.improvement_plan.actions.map(action => `<li>${escapeHtml(action)}</li>`).join('')}</ul>`;
    if (data.source) {
      const detail = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = '가져온 공고 본문 확인';
      const text = document.createElement('textarea');
      text.rows = 12;
      text.setAttribute('aria-label', '추출된 공고 본문 수정');
      text.style.whiteSpace = 'pre-wrap';
      text.value = data.source.text;
      const warning = document.createElement('p');
      warning.textContent = data.source.warning || '분석에 사용된 공고 본문입니다.';
      const reuse = document.createElement('button');
      reuse.textContent = '수정한 본문으로 재분석';
      reuse.addEventListener('click', () => {
        document.querySelector('#job-url').value = '';
        document.querySelector('#job').value = text.value;
        mode.value = 'text';
        updateMode();
        button.click();
      });
      detail.append(summary, warning, text, reuse);
      detail.open = Boolean(data.source.ocr_images);
      result.append(detail);
    }
  } catch (error) {
    result.innerHTML = '<p>이미지 업로드 또는 텍스트 직접 입력으로 전환해 다시 분석할 수 있습니다.</p>';
    errorBox.textContent = error.message;
  } finally {
    button.disabled = false;
    button.firstChild.textContent = '에이전트 분석 시작 ';
  }
});

// 문서용 실행 화면을 재현할 때만 샘플 분석을 자동 실행한다.
if (new URLSearchParams(window.location.search).get('demo') === '1') {
  mode.value = 'text'; updateMode();
  button.click();
}
