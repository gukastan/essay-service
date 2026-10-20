# Next.js v2 변경 전 기준선

2026-10-20 전환 이전의 코드·작업 문서는 Git 커밋 `c5299e954d0ff1b0848dad238e7b731ef078bb51`에 보존돼 있다. 아래는 당시 원문을 가리키는 커밋 고정 링크다. 현재 Python·Vue 구현 지시로 사용하지 않는다.

- [AGENTS.md](https://github.com/gukastan/essay-service/blob/c5299e954d0ff1b0848dad238e7b731ef078bb51/AGENTS.md)
- [START_OMO_V2.md](https://github.com/gukastan/essay-service/blob/c5299e954d0ff1b0848dad238e7b731ef078bb51/START_OMO_V2.md)
- [README.md](https://github.com/gukastan/essay-service/blob/c5299e954d0ff1b0848dad238e7b731ef078bb51/README.md)
- [docs/PRD_V2.md](https://github.com/gukastan/essay-service/blob/c5299e954d0ff1b0848dad238e7b731ef078bb51/docs/PRD_V2.md)
- [docs/TECH_DESIGN_V2.md](https://github.com/gukastan/essay-service/blob/c5299e954d0ff1b0848dad238e7b731ef078bb51/docs/TECH_DESIGN_V2.md)
- [docs/BACKLOG_V2.md](https://github.com/gukastan/essay-service/blob/c5299e954d0ff1b0848dad238e7b731ef078bb51/docs/BACKLOG_V2.md)
- [docs/qa-v2.md](https://github.com/gukastan/essay-service/blob/c5299e954d0ff1b0848dad238e7b731ef078bb51/docs/qa-v2.md)
- [docs/jira-v2.json](https://github.com/gukastan/essay-service/blob/c5299e954d0ff1b0848dad238e7b731ef078bb51/docs/jira-v2.json)

- [Jira 변경 전 스냅샷](jira-before-migration.json): ESSAY-8~17의 제목·본문·상태·부모·연결. 댓글은 변경하지 않으며 이 스냅샷에는 포함되지 않는다.
- [당시 로컬 Jira 매핑](jira-v2.json)
- [이전 기술 결정과 제공자 검증](../../decisions/langgraph-v2.md)
- [현재 전환 계획](../../ASSIGNMENT_MIGRATION.md)

루트 src/·tests/·의존성·v1 QA·run-7 승인·ESSAY-9 증거는 현재 작업에서도 그대로 보존한다. 완료된 ESSAY-1~7·9의 Jira 본문/상태는 수정하지 않는다.
