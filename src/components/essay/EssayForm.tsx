import type { DraftField, DraftRequest, FieldErrors } from "@/shared/contracts";

export const essayFields = [
  {
    name: "company",
    label: "기업명",
    placeholder: "예: 네이버",
    hint: "지원할 기업을 알려 주세요.",
    rows: 0,
  },
  {
    name: "role",
    label: "지원 직무",
    placeholder: "예: 서비스 기획",
    hint: "맡고 싶은 일을 알려 주세요.",
    rows: 0,
  },
  {
    name: "question",
    label: "자기소개서 문항",
    placeholder: "지원하는 직무와 관련된 경험과 본인의 강점을 작성해 주세요.",
    hint: "지원서에 있는 문항을 그대로 입력해 주세요.",
    rows: 3,
  },
  {
    name: "experience",
    label: "나의 경험",
    placeholder:
      "어떤 상황이었나요?\n내가 맡은 역할과 직접 한 행동은 무엇인가요?\n어떤 결과가 있었고, 무엇을 배웠나요?",
    hint: "작은 경험도 괜찮아요. 실제로 한 일과 배운 점을 구체적으로 적어 주세요.",
    rows: 7,
  },
] as const;

type Props = {
  readonly values: DraftRequest;
  readonly errors: FieldErrors;
  readonly pending: boolean;
  readonly onChange: (field: DraftField, value: string) => void;
  readonly onSubmit: () => void;
};

export function EssayForm({ values, errors, pending, onChange, onSubmit }: Props) {
  return (
    <section className="panel" aria-labelledby="input-heading">
      <div className="section-heading">
        <span className="step">01</span>
        <h2 id="input-heading">경험 꺼내기</h2>
      </div>
      <p className="section-description">네 가지 재료로 나다운 초안을 시작해 보세요.</p>
      <form
        noValidate
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
        aria-busy={pending}
      >
        <fieldset disabled={pending}>
          <legend className="sr-only">자기소개서 작성 정보</legend>
          <div className="fields">
            {essayFields.map((field) => {
              const error = errors[field.name];
              const common = {
                id: field.name,
                name: field.name,
                value: values[field.name],
                required: true,
                placeholder: field.placeholder,
                "aria-invalid": Boolean(error),
                "aria-describedby": `${field.name}-hint${error ? ` ${field.name}-error` : ""}`,
              };
              return (
                <div className={`field ${field.rows ? "field-wide" : ""}`} key={field.name}>
                  <label htmlFor={field.name}>
                    {field.label}
                    <span className="required">필수</span>
                  </label>
                  {field.rows ? (
                    <textarea
                      {...common}
                      rows={field.rows}
                      onChange={(event) => onChange(field.name, event.target.value)}
                    />
                  ) : (
                    <input
                      {...common}
                      type="text"
                      onChange={(event) => onChange(field.name, event.target.value)}
                    />
                  )}
                  <p className="field-hint" id={`${field.name}-hint`}>
                    {field.hint}
                  </p>
                  {error && (
                    <p className="field-error" id={`${field.name}-error`}>
                      {error}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
          <button className="button primary generate-button" type="submit">
            {pending ? (
              <>
                <span className="spinner" aria-hidden="true" />
                초안 작성 중…
              </>
            ) : (
              <>
                초안 만들기 <span aria-hidden="true">↗</span>
              </>
            )}
          </button>
        </fieldset>
        <p className="form-note">작성한 내용은 이 화면에서만 유지돼요. 새로고침하면 사라집니다.</p>
      </form>
    </section>
  );
}
