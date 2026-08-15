# Future RAG Boundary

Phase 11 documents but does not implement clinical knowledge retrieval or a chatbot.

## Future architecture

```text
approved/licensed knowledge source
  -> ingestion and document validation
  -> versioned chunking
  -> deferred embedding model
  -> deferred vector store
  -> retrieval with authorization and freshness filters
  -> evidence ranking and citation/provenance
  -> bounded answer generation
  -> safety validation and abstention
```

The SRS does not specify a knowledge corpus, licensing arrangement, chunking strategy, embedding model, vector database, LLM provider, freshness policy, or citation format. Each remains **Not specified in supplied requirements — deferred decision**.

A future retrieval system must distinguish retrieved evidence from generated wording, preserve document/version provenance, prevent cross-patient data leakage, refuse unsupported clinical requests, and never answer from unverified or unauthorized records. No ingestion, embeddings, vector database, retrieval call, or external model API exists in Phase 11.
