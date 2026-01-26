from app.data.vector_db import LegalKnowledgeBase

def test_brain():
    print("🧠 Waking up the Legal Knowledge Base...")
    kb = LegalKnowledgeBase()
    
    # The Query
    query = "What rules apply to negative option features or recurring subscriptions?"
    
    print(f"\n🔎 Searching for: '{query}'")
    results = kb.search_laws(query)
    
    print("\n📄 RETRIEVED CONTEXT:")
    print(results)
    
    if "SOURCE" in results:
        print("\n✅ SUCCESS: The agent is reading your PDFs!")
    else:
        print("\n❌ FAILURE: No documents found. Did you run vector_db.py?")

if __name__ == "__main__":
    test_brain()