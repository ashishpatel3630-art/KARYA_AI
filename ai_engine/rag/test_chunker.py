from rag.chunker import DocumentChunker


text = """
KARYA AI Industrial Maintenance Report.

Pump P-101 is operating under abnormal conditions.
The equipment temperature is 85 C.
The measured vibration is 7.2 mm/s.
The current equipment status is Critical.
Maintenance inspection is required immediately.
The bearing assembly should be inspected.
The vibration source should be identified.
Preventive maintenance should be scheduled.
"""


chunker = DocumentChunker(
    chunk_size=100,
    chunk_overlap=20,
)

chunks = chunker.chunk(text)


print(f"TOTAL CHUNKS: {len(chunks)}")

for chunk in chunks:
    print("\n--------------------")
    print(f"CHUNK ID: {chunk.chunk_id}")
    print("--------------------")
    print(chunk.content)
