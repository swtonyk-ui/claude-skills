# claude-skills

## paper-guide

논문 PDF를 올리면 원문 순서대로 **문단별 한글 해설본**(번역 아님)을 PDF로 만들어 주는 스킬.
해부학·의학 용어는 영어 유지, 논문 figure 포함, 선택적으로 케이스(판독문)와 연결.

### Claude Code

```
/plugin marketplace add swtonyk-ui/claude-skills
/plugin install paper-guide@swtonyk-skills
```

사용: 논문 PDF 경로를 주고 "논문 해설본 만들어줘" (+ 케이스 한두 줄).

### claude.ai

`plugins/paper-guide/skills/paper-guide` 폴더를 zip으로 묶어 Settings → Capabilities → Skills에서 업로드 (코드 실행 켜기 필요).

### 주의

해설본에는 원 논문 그림이 들어가므로 개인 학습용으로만 쓰고 재배포하지 마세요.
