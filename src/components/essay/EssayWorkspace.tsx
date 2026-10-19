"use client";

import ky, { TimeoutError } from "ky";
import { useRef, useState } from "react";
import { normalizeLineEndings } from "@/shared/characters";
import {
  assertNever,
  type DraftField,
  type DraftRequest,
  draftRequestSchema,
  draftResponseSchema,
  type FieldErrors,
} from "@/shared/contracts";
import { EssayForm, essayFields } from "./EssayForm";
import { type EssayDraft, EssayResult } from "./EssayResult";

type Notice = { readonly kind: "error" | "info"; readonly message: string } | null;
const emptyRequest: DraftRequest = { company: "", role: "", question: "", experience: "" };

export function EssayWorkspace() {
  const [values, setValues] = useState<DraftRequest>(emptyRequest);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [pending, setPending] = useState(false);
  const [notice, setNotice] = useState<Notice>(null);
  const [result, setResult] = useState<EssayDraft | null>(null);
  const [resultVersion, setResultVersion] = useState(0);
  const inFlight = useRef(false);

  function changeField(field: DraftField, value: string) {
    setValues((previous) => ({ ...previous, [field]: normalizeLineEndings(value) }));
    setErrors((previous) => {
      const next = { ...previous };
      delete next[field];
      return next;
    });
  }

  async function generate() {
    if (inFlight.current) return;
    const input = draftRequestSchema.safeParse(values);
    if (!input.success) {
      const nextErrors: FieldErrors = {};
      for (const field of essayFields) {
        if (values[field.name].trim().length === 0)
          nextErrors[field.name] = `${field.label} 항목을 입력해 주세요.`;
      }
      setErrors(nextErrors);
      setNotice({ kind: "error", message: "비어 있는 필수 항목을 확인해 주세요." });
      const first = essayFields.find((field) => nextErrors[field.name]);
      if (first) document.getElementById(first.name)?.focus();
      return;
    }
    inFlight.current = true;
    setPending(true);
    setErrors({});
    setNotice(null);
    const request = { ...input.data };
    try {
      const response = await ky.post("/api/drafts", {
        json: request,
        retry: 0,
        timeout: 75_000,
        throwHttpErrors: false,
      });
      const payload: unknown = await response.json();
      const parsed = draftResponseSchema.safeParse(payload);
      if (!parsed.success) {
        setNotice({
          kind: "error",
          message: "초안을 불러오지 못했어요. 잠시 후 다시 시도해 주세요.",
        });
        return;
      }
      const data = parsed.data;
      switch (data.status) {
        case "ready":
          if (!response.ok) {
            setNotice({
              kind: "error",
              message: "요청을 완료하지 못했어요. 잠시 후 다시 시도해 주세요.",
            });
            return;
          }
          setResult({ request, text: normalizeLineEndings(data.draft) });
          setResultVersion((previous) => previous + 1);
          setNotice({
            kind: "info",
            message: "초안이 준비됐어요. 요청 당시의 경험과 비교하며 다듬어 보세요.",
          });
          break;
        case "needs_input":
          setNotice({ kind: "info", message: `경험을 조금 더 알려 주세요. ${data.message}` });
          break;
        case "error":
          setNotice({ kind: "error", message: data.message });
          setErrors(data.fieldErrors ?? {});
          break;
        default:
          assertNever(data);
      }
    } catch (error) {
      if (error instanceof TimeoutError) {
        setNotice({
          kind: "error",
          message:
            "응답을 기다리는 시간이 길어졌어요. 입력은 그대로 남아 있으니 잠시 후 다시 시도해 주세요.",
        });
      } else if (error instanceof Error) {
        setNotice({
          kind: "error",
          message: "연결에 문제가 생겼어요. 네트워크를 확인한 뒤 다시 시도해 주세요.",
        });
      } else {
        setNotice({ kind: "error", message: "요청을 완료하지 못했어요. 다시 시도해 주세요." });
      }
    } finally {
      inFlight.current = false;
      setPending(false);
    }
  }

  return (
    <>
      <div className="feedback-region">
        {pending && (
          <div className="notice info" role="status">
            <strong>경험을 문장으로 정리하고 있어요.</strong>
            <span>분량을 맞추는 시간까지 약 1분 정도 걸릴 수 있어요.</span>
          </div>
        )}
        {notice && (
          <div
            className={`notice ${notice.kind}`}
            role={notice.kind === "error" ? "alert" : "status"}
          >
            {notice.message}
          </div>
        )}
      </div>
      <div className="workspace">
        <EssayForm
          values={values}
          errors={errors}
          pending={pending}
          onChange={changeField}
          onSubmit={() => {
            void generate();
          }}
        />
        <EssayResult
          key={resultVersion}
          result={result}
          pending={pending}
          onEdit={(text) => setResult((previous) => (previous ? { ...previous, text } : previous))}
        />
      </div>
    </>
  );
}
