def group_citation_locations(locations):
    """Group chunk-level citations into one location per document."""
    grouped = {}

    for location in locations:
        document_name = location["document"]
        document_key = str(location.get("document_id") or document_name)
        page = location.get("page")
        score = float(location.get("score") or 0)

        entry = grouped.setdefault(
            document_key,
            {
                "document": document_name,
                "pages": [],
                "score": score,
            },
        )

        if page is not None and page not in entry["pages"]:
            entry["pages"].append(page)
        entry["score"] = max(entry["score"], score)

    results = []
    for entry in grouped.values():
        entry["pages"].sort()
        entry["score"] = round(entry["score"], 3)
        results.append(entry)

    return results
