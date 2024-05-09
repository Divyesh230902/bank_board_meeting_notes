from rbi_mom_v1 import RBI_Summarizer


test_summarizer = RBI_Summarizer('pdf')

final_output = test_summarizer.summarize_documents()

print(final_output)