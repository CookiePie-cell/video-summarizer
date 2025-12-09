import typing_extensions as typing

class QnAItem(typing.TypedDict):
    question: str
    answer: str

class SentimentAnalysis(typing.TypedDict):
    sentiment: str
    description: str

class NamedEntities(typing.TypedDict):
    people: list[str]
    places: list[str]
    organizations: list[str]

class ContentClassification(typing.TypedDict):
    type: str
    characteristics: list[str]

class SummaryResponse(typing.TypedDict):
    summary: str
    bulletPoints: list[str]
    topicIdentification: list[str]
    quoteExtraction: list[str]
    characterIdentification: list[str]
    sentimentAnalysis: SentimentAnalysis
    qna: list[QnAItem]
    namedEntities: NamedEntities
    contentClassification: ContentClassification