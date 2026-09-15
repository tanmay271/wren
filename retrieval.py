import anthropic
from llama_index.core import VectorStoreIndex, PromptTemplate
from llama_index.llms.anthropic import Anthropic as AnthropicLLM

_HR_PROMPT = PromptTemplate(
    "You are a knowledgeable HR assistant for Meridian Semiconductor. "
    "Your role is to help employees understand company policies, benefits, and procedures.\n\n"
    "Use only the provided HR policy excerpts to answer the question. "
    "Be professional, concise, and accurate. "
    "If the answer is not covered in the excerpts, say so clearly and suggest "
    "the employee contact HR directly.\n\n"
    "HR Policy Excerpts:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n\n"
    "Employee Question: {query_str}\n\n"
    "Answer:"
)


def get_answer(
    index: VectorStoreIndex,
    query: str,
    api_key: str,
) -> tuple[str, list[dict]]:
    """Query the index and return (answer_text, source_chunks)."""
    llm = AnthropicLLM(
        model="claude-sonnet-4-6",
        api_key=api_key,
        max_tokens=1024,
    )
    engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=3,
        text_qa_template=_HR_PROMPT,
    )
    response = engine.query(query)

    sources = [
        {
            "text": node.node.get_content(),
            "score": round(node.score or 0.0, 3),
            "page": node.node.metadata.get(
                "page_label",
                node.node.metadata.get("page", "—"),
            ),
        }
        for node in response.source_nodes
    ]
    return str(response), sources


def generate_faqs(index: VectorStoreIndex, api_key: str) -> list[str]:
    """Analyze indexed document and return 8-9 employee-specific FAQ questions."""
    nodes = list(index.storage_context.docstore.docs.values())
    if not nodes:
        return []

    # Collect up to ~5000 chars of document text as context for Claude
    samples: list[str] = []
    total = 0
    for node in nodes[:25]:
        content = node.get_content().strip()
        if content and total < 5000:
            chunk = content[:300]
            samples.append(chunk)
            total += len(chunk)

    if not samples:
        return []

    sample_text = "\n\n---\n\n".join(samples)

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": (
                "You are analyzing an HR policy document. Based on the following excerpts, "
                "generate exactly 9 specific, realistic questions that an employee would ask. "
                "Questions must be grounded in the actual content — reference real policy details "
                "like specific timeframes, procedures, benefit types, or named policies in the text. "
                "Do not generate generic HR questions.\n\n"
                f"Document excerpts:\n{sample_text}\n\n"
                "Return ONLY a numbered list of 9 questions (1. ...? 2. ...? etc.). "
                "No preamble, no explanation, no trailing text."
            ),
        }],
    )

    raw = msg.content[0].text.strip()
    questions: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if line and line[0].isdigit() and ". " in line:
            q = line.split(". ", 1)[1].strip()
            if q:
                questions.append(q)

    return questions[:9]
