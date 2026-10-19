import { useRef, useState } from "react";
import {
  countCharacters,
  isValidDraftLength,
  MAX_CHARACTERS,
  MIN_CHARACTERS,
  normalizeLineEndings,
} from "@/shared/characters";
import type { DraftRequest } from "@/shared/contracts";

export type EssayDraft = {
  readonly request: DraftRequest;
  readonly text: string;
};

type Props = {
  readonly result: EssayDraft | null;
  readonly pending: boolean;
  readonly onEdit: (text: string) => void;
};

export function EssayResult({ result, pending, onEdit }: Props) {
  const [copyMessage, setCopyMessage] = useState("");
  const [copying, setCopying] = useState(false);
  const copyVersion = useRef(0);
  const text = result?.text ?? "";
  const count = countCharacters(text);
  const valid = isValidDraftLength(count);

  async function copyDraft() {
    const version = ++copyVersion.current;
    setCopying(true);
    setCopyMessage("");
    try {
      await navigator.clipboard.writeText(text);
      if (version === copyVersion.current) setCopyMessage("현재 초안을 복사했어요.");
    } catch (error) {
      if (error instanceof Error && version === copyVersion.current) {
        setCopyMessage("복사하지 못했어요. 초안 내용을 선택한 뒤 직접 복사해 주세요.");
      }
    } finally {
      setCopying(false);
    }
  }

  return (
    <section className="panel result-panel" aria-labelledby="result-heading">
      <div className="section-heading">
        <span className="step">02</span>
        <h2 id="result-heading">문장 다듬기</h2>
        <span className="length-badge">801–1,000자</span>
      </div>
      <p className="section-description">내 경험과 비교하고, 내 목소리로 마무리하세요.</p>
      {result ? (
        <>
          <div className="source-block">
            <div className="source-header">
              <h3>요청 당시의 경험</h3>
              <span>
                {result.request.company} · {result.request.role}
              </span>
            </div>
            <p className="original-experience">{result.request.experience}</p>
          </div>
          <div className="draft-heading">
            <label htmlFor="draft">초안 편집</label>
            <span
              className={valid ? "count valid" : "count warning"}
              aria-live="polite"
              aria-atomic="true"
            >
              {count.toLocaleString("ko-KR")} / {MAX_CHARACTERS.toLocaleString("ko-KR")}자
            </span>
          </div>
          <textarea
            id="draft"
            className="draft-editor"
            value={text}
            rows={17}
            disabled={pending}
            aria-describedby="count-help draft-guidance"
            onChange={(event) => {
              copyVersion.current += 1;
              setCopyMessage("");
              onEdit(normalizeLineEndings(event.target.value));
            }}
          />
          <p className="field-hint" id="count-help">
            공백·줄바꿈 포함 · 이모지도 같은 기준으로 계산해요.
          </p>
          <p
            id="draft-guidance"
            className={`length-guidance ${valid ? "valid" : "warning"}`}
            aria-live="polite"
          >
            {valid
              ? "권장 분량이에요. 경험에 없는 내용이 없는지 확인해 주세요."
              : count < MIN_CHARACTERS
                ? `${MIN_CHARACTERS - count}자 이상 더 작성하면 권장 분량이 돼요. 지금 내용도 복사할 수 있어요.`
                : `${count - MAX_CHARACTERS}자를 줄이면 권장 분량이 돼요. 지금 내용도 복사할 수 있어요.`}
          </p>
          <div className="copy-row">
            <button
              type="button"
              className="button secondary"
              disabled={pending || copying}
              onClick={() => {
                void copyDraft();
              }}
            >
              {copying ? "복사 중…" : "초안 복사"}
            </button>
            <p className="copy-feedback" role="status">
              {copyMessage}
            </p>
          </div>
        </>
      ) : (
        <div className="empty-result">
          <span className="document-mark" aria-hidden="true">
            Aa
          </span>
          <h3>당신의 이야기가 들어올 자리</h3>
          <p>
            왼쪽에 경험을 적어 주세요.
            <br />
            지원하는 기업과 문항에 맞춰
            <br />
            검토할 수 있는 초안으로 정리해 드릴게요.
          </p>
          <div className="empty-rule" />
          <p className="empty-note">
            좋은 문장의 시작은
            <br />
            실제로 해 본 일에서 나와요.
          </p>
        </div>
      )}
    </section>
  );
}
