import strawberry
from app.rag import answer_question


@strawberry.type
class AnswerType:
    text: str
    sources: list[str]


@strawberry.type
class Query:
    @strawberry.field
    def ask_question(self, question: str) -> AnswerType:
        result = answer_question(question)
        return AnswerType(text=result.text, sources=result.sources)

    @strawberry.field
    def health(self) -> str:
        return "ok"


schema = strawberry.Schema(query=Query)
