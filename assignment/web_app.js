import {fields, normalize, count, safeUrl, parseResponse} from './web_contract.js';
const {createApp, ref, reactive, computed} = window.Vue;
createApp({setup() {
  const input = reactive(Object.fromEntries(fields.map(f => [f.key, ''])));
  const errors = ref({});
  const busy = ref(false);
  const notice = ref(null);
  const result = ref(null);
  const edited = ref('');
  const copied = ref('');
  let active = null;
  const editedCount = computed(() => count(edited.value));
  const changed = computed(() => result.value && normalize(edited.value) !== normalize(result.value.response.draft));
  const fieldLabel = key => fields.find(f => f.key === key)?.label ?? key;
  const claimLabel = kind => ({user_fact:'나의 사실', company_fact:'회사 사실', interpretation:'현재 해석', future_plan:'미래 계획'})[kind];
  const criterionLabel = key => ({contract_evidence:'근거 연결', user_factuality:'개인 사실성', company_factuality:'회사 사실성', question_coverage:'문항 충족', job_fit:'직무 연결', length:'분량', expression_kind:'사실·해석 구분'})[key] ?? key;
  const date = value => new Intl.DateTimeFormat('ko-KR', {dateStyle:'medium'}).format(new Date(value));
  function cancel() {
    if (active) { active.reason = 'cancel'; active.controller.abort(); }
  }
  async function submit() {
    if (busy.value) return;
    errors.value = {};
    for (const f of fields) {
      if ((!f.optional && !input[f.key].trim()) || count(input[f.key]) > f.limit)
        errors.value[f.key] = `내용을 입력해 주세요. 최대 ${f.limit.toLocaleString()}자입니다.`;
    }
    if (input.jobPostingUrl.trim() && !safeUrl(input.jobPostingUrl)) errors.value.jobPostingUrl = '올바른 HTTP 또는 HTTPS 주소를 입력해 주세요.';
    if (Object.keys(errors.value).length) {
      await window.Vue.nextTick();
      document.getElementById(Object.keys(errors.value)[0]).focus();
      return;
    }
    const snapshot = Object.fromEntries(fields.map(f => [f.key, normalize(input[f.key])]));
    const request = {controller: new AbortController(), reason: ''};
    active = request; busy.value = true; notice.value = null; copied.value = '';
    const timer = setTimeout(() => { request.reason = 'timeout'; request.controller.abort(); }, 195000);
    try {
      const response = await fetch('/api/drafts', {method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify(snapshot), signal:request.controller.signal});
      const data = parseResponse(await response.json(), response.status, snapshot);
      if (request.controller.signal.aborted) return;
      switch (data.status) {
        case 'ready': result.value = {response:data, snapshot}; edited.value = normalize(data.draft); break;
        case 'review_needed':
          result.value = {response:data, snapshot}; edited.value = normalize(data.draft);
          notice.value = {kind:'review_needed', title:'이번 초안은 검토가 필요합니다', message:'기준을 충족하지 못한 항목을 확인하고 제출 전에 수정해 주세요.', reviewIssues:data.reviewIssues};
          break;
        case 'needs_input': notice.value = {kind:'needs_input', title:'추가 정보가 필요합니다', message:data.message, questions:data.questions, missingFields:data.missingFields}; break;
        case 'error': notice.value = {kind:'error', title:'생성을 완료하지 못했습니다', message:data.message}; break;
      }
    } catch {
      notice.value = {kind:'error', title: request.reason === 'cancel' ? '생성을 취소했습니다' : request.reason === 'timeout' ? '처리 시간이 초과됐습니다' : '응답을 확인할 수 없습니다', message:'입력과 이전 결과는 유지됩니다. 내용을 확인한 뒤 다시 시도해 주세요.'};
    } finally {
      clearTimeout(timer); active = null; busy.value = false;
    }
  }
  async function copy() {
    try { await navigator.clipboard.writeText(normalize(edited.value)); copied.value = '현재 편집 내용을 복사했습니다.'; }
    catch { copied.value = '복사 권한이 없습니다. 초안 내용을 선택해 직접 복사해 주세요.'; }
  }
  return {fields,input,errors,busy,notice,result,edited,copied,editedCount,changed,fieldLabel,claimLabel,criterionLabel,date,submit,cancel,copy,count};
}}).mount('#app');
