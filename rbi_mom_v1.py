
from pdf2image import convert_from_path
from paddleocr import PaddleOCR
import os
from langchain_community.llms import Ollama

pdf_ls = os.listdir("pdf")

# Path to the PDF file
for pdf in pdf_ls:
    pdf_path = f"pdf/{pdf}"
    if not os.path.exists("Docs"):
        os.mkdir("Docs")
    doc_path = f"Docs/{pdf_path[4:-4:]}"
    if not os.path.exists(doc_path):
        os.mkdir(doc_path)
    # Convert PDF pages to images
    images = convert_from_path(pdf_path)

    # Save each image
    for i, img in enumerate(images):
        img.save(f"{doc_path}/page_{i+1:02d}.jpg")

    # Print a success message
    print(f"{len(images)} images were successfully extracted from {pdf_path}.")

llm = Ollama(model="mixtral")

cleaned_ls = []
ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to load model into memory
doc_ls = sorted(os.listdir("Docs/"))
for i, doc in enumerate(doc_ls):
    page_ls = sorted(os.listdir(f"Docs/{doc}"))
    print(f"processing document ----> Docs/{doc}")
    strings = []
    for page in page_ls:
        print(f"processing page ----> Docs/{doc}/{page}")
        img_path = os.path.join(f"Docs/{doc}", page)
        # print(img_path)
        result = ocr.ocr(img_path, cls=True)
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                print("<----Extracted Text---->\n",line[1][0])
                strings.append(line[1][0])
    final_doc = ('\n').join(strings)
    print(final_doc)
    cleaned_txt = llm.invoke(f"{final_doc}; convert the given document in the format of Minutes of meaning")
    print("<----Cleaned Text---->\n", cleaned_txt)
    cleaned_ls.append(cleaned_txt)
    if i > 6:
        break
print(len(cleaned_ls))


master_context = ('\n\n').join(cleaned_ls)
# Open the file in write mode
with open('output.txt', 'w') as file:
    # Write a string to the file
    file.write(master_context)

analysis_doc = llm.invoke(f"read the given document {master_context}; and write an analysis report on that")

# Open the file in write mode
with open('analysis_report.txt', 'w') as file:
    # Write a string to the file
    file.write(analysis_doc)



