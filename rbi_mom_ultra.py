from pdf2image import convert_from_path
from paddleocr import PaddleOCR
import os
from langchain_community.llms import Ollama
from concurrent.futures import ThreadPoolExecutor

class BankBoardMeetingNotesProcessor:
    def __init__(self, pdf_dir="pdf", docs_dir="Docs", output_dir="output"):
        self.pdf_dir = pdf_dir
        self.docs_dir = docs_dir
        self.output_dir = output_dir
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
        self.llm = Ollama(model="mixtral")

        # Ensure directories exist
        for dir_path in [self.pdf_dir, self.docs_dir, self.output_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def convert_pdf_to_images(self, pdf_path):
        try:
            images = convert_from_path(pdf_path)
            doc_path = f"{self.docs_dir}/{pdf_path[4:-4:]}"
            if not os.path.exists(doc_path):
                os.mkdir(doc_path)
            for i, img in enumerate(images):
                img.save(f"{doc_path}/page_{i+1:02d}.jpg")
            print(f"{len(images)} images were successfully extracted from {pdf_path}.")
        except Exception as e:
            print(f"Error converting PDF to images: {e}")

    def process_images(self, doc_path):
        try:
            page_ls = sorted(os.listdir(doc_path))
            strings = []
            for page in page_ls:
                img_path = os.path.join(doc_path, page)
                result = self.ocr.ocr(img_path, cls=True)
                for idx in range(len(result)):
                    res = result[idx]
                    for line in res:
                        strings.append(line[1][0])
            final_doc = ('\n').join(strings)
            cleaned_txt = self.llm.invoke(f"Document: {final_doc}; Segregate Minutes of Meeting, Agenda and Action Points present in the given documnet.")
            return cleaned_txt
        except Exception as e:
            print(f"Error processing images: {e}")
            return None

    def process_all_documents(self):
        pdf_ls = os.listdir(self.pdf_dir)
        with ThreadPoolExecutor() as executor:
            for pdf in pdf_ls:
                pdf_path = f"{self.pdf_dir}/{pdf}"
                self.convert_pdf_to_images(pdf_path)
                doc_path = f"{self.docs_dir}/{pdf_path[4:-4:]}"
                cleaned_txt = self.process_images(doc_path)
                if cleaned_txt:
                    with open(f"{self.output_dir}/{pdf_path[4:-4:]}.txt", 'w') as file:
                        file.write(cleaned_txt)

if __name__ == "__main__":
    processor = BankBoardMeetingNotesProcessor()
    processor.process_all_documents()
