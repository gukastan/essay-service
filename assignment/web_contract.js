export const normalize = value => value.replace(/\r\n?/g, '\n');
export const count = value => [...normalize(value)].length;
export const fields = [
  {key: 'company', label: '기업', limit: 120},
  {key: 'role', label: '직무', limit: 160},
  {key: 'question', label: '자기소개서 문항', limit: 3000, multiline: true},
  {key: 'experience', label: '나의 경험', limit: 12000, multiline: true},
  {key: 'jobPostingUrl', label: '공고 URL (선택)', limit: 2048, optional: true},
  {key: 'jobPostingText', label: '공고 본문 (선택)', limit: 16000, optional: true, multiline: true},
];
export function safeUrl(value) {
  try {
    const u = new URL(value);
    return ['https:', 'http:'].includes(u.protocol) && !u.username && !u.password && !/\s/.test(value);
  } catch { return false; }
}
const text = value => typeof value === 'string' && value.trim().length > 0;
const list = (value, check) => Array.isArray(value) && value.every(check);
const ids = value => list(value, text);
const item = value => value && text(value.id) && text(value.text);
export function parseResponse(data, status, snapshot) {
  const invalid = () => { throw new Error('INVALID_RESPONSE'); };
  if (!data || !/^[0-9a-f]{8}-[0-9a-f-]{27}$/i.test(data.requestId ?? '')) invalid();
  switch (data.status) {
    case 'needs_input':
      if (status !== 200 || !text(data.message) || !ids(data.questions) || !data.questions.length ||
          !ids(data.missingFields) || !data.missingFields.length ||
          !data.missingFields.every(key => fields.some(f => f.key === key)) ||
          !['COMPANY_AMBIGUOUS', 'JOB_EVIDENCE_MISSING', 'EXPERIENCE_INSUFFICIENT', 'EVIDENCE_INSUFFICIENT'].includes(data.reasonCode)) invalid();
      break;
    case 'error':
      if (status < 400 || !text(data.message) || !['INVALID_INPUT', 'V2_DISABLED', 'LENGTH_VALIDATION_FAILED', 'QUALITY_CHECK_FAILED', 'CONFIG_ERROR', 'MODEL_ERROR', 'SEARCH_ERROR', 'INVALID_RESPONSE', 'TIMEOUT', 'CANCELLED', 'BUDGET_EXCEEDED'].includes(data.code)) invalid();
      if (['QUALITY_CHECK_FAILED', 'LENGTH_VALIDATION_FAILED'].includes(data.code) && status !== 422) invalid();
      break;
    case 'ready': {
      if (status !== 200 || !text(data.draft) || count(data.draft) !== data.characterCount ||
          data.characterCount < 801 || data.characterCount > 1000 || data.reviewSummary !== '생성 당시 검토 통과') invalid();
      if (!list(data.sources, s => s && text(s.id) && text(s.title) && text(s.excerpt) &&
          text(s.checkedAt) && Number.isFinite(Date.parse(s.checkedAt)) &&
          ['official', 'user_provided'].includes(s.kind) &&
          (s.url ? safeUrl(s.url) : s.kind === 'user_provided'))) invalid();
      const e = data.evidence;
      if (!e || !list(e.companyFacts, f => item(f) && ids(f.sourceIds)) ||
          !list(e.jobRequirements, f => item(f) && ids(f.sourceIds)) ||
          !list(e.claimMap, c => item(c) && ids(c.evidenceIds) && ['user_fact', 'company_fact', 'interpretation', 'future_plan'].includes(c.kind)) ||
          !list(e.fitReasons, f => f && text(f.reason) && ids(f.experienceEvidenceIds) && ids(f.jobRequirementIds)) ||
          !list(e.experienceEvidence, x => x && text(x.id) && text(x.quote) && Number.isInteger(x.start) &&
            Number.isInteger(x.end) && x.start >= 0 && x.end > x.start &&
            [...normalize(snapshot.experience)].slice(x.start, x.end).join('') === normalize(x.quote))) invalid();
      break;
    }
    default: invalid();
  }
  return data;
}
