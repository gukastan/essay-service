import { EssayWorkspace } from "@/components/essay/EssayWorkspace";

export default function Home() {
  return (
    <>
      <a className="skip-link" href="#main">
        작성 화면으로 건너뛰기
      </a>
      <header className="site-header">
        <div className="header-inner">
          <span className="wordmark">
            문장, 나로부터
            <span className="brand-dot" aria-hidden="true" />
          </span>
          <span className="header-note">자기소개서 작업실</span>
        </div>
      </header>
      <main id="main" className="page-shell">
        <div className="intro">
          <div>
            <p className="eyebrow">나의 경험에서 시작하는 자기소개서</p>
            <h1>
              경험은 그대로,
              <br />
              표현은 더 선명하게.
            </h1>
            <p className="intro-copy">
              막막한 첫 문장부터 차근차근.
              <br className="mobile-break" /> 당신이 해 온 일을 초안으로 정리해 보세요.
            </p>
          </div>
          <div className="intro-aside">
            <span>경험 입력</span>
            <span aria-hidden="true">→</span>
            <span>초안 작성</span>
            <span aria-hidden="true">→</span>
            <span>직접 다듬기</span>
          </div>
        </div>
        <EssayWorkspace />
        <footer className="page-footer">
          <p>
            AI가 작성한 초안은 실제 경험과 다를 수 있어요. 제출 전 사실과 표현을 꼭 확인해 주세요.
          </p>
          <span>당신의 경험, 당신의 문장.</span>
        </footer>
      </main>
    </>
  );
}
